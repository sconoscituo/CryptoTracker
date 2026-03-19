from typing import Optional
from app.config import settings


class TelegramNotifier:
    """텔레그램 봇을 통한 가격 알림 발송"""

    def __init__(self):
        self.token = settings.telegram_bot_token
        self._bot = None

    def _get_bot(self):
        """텔레그램 봇 인스턴스 지연 초기화"""
        if not self._bot and self.token:
            from telegram import Bot
            self._bot = Bot(token=self.token)
        return self._bot

    async def send_price_alert(
        self,
        chat_id: str,
        symbol: str,
        current_price: float,
        target_price: float,
        direction: str,
    ) -> bool:
        """
        목표가 도달 시 텔레그램 알림 발송
        - direction: "above" = 목표가 이상, "below" = 목표가 이하
        """
        bot = self._get_bot()
        if not bot or not chat_id:
            return False

        direction_text = "이상 돌파" if direction == "above" else "이하 하락"
        symbol_upper = symbol.upper()

        message = (
            f"🔔 *CryptoTracker 가격 알림*\n\n"
            f"코인: *{symbol_upper}*\n"
            f"현재가: *${current_price:,.4f}*\n"
            f"목표가: ${target_price:,.4f} {direction_text}\n\n"
            f"설정하신 목표가에 도달했습니다!"
        )

        try:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="Markdown",
            )
            return True
        except Exception:
            return False

    async def send_portfolio_summary(
        self,
        chat_id: str,
        summary: dict,
    ) -> bool:
        """포트폴리오 일일 요약 발송"""
        bot = self._get_bot()
        if not bot or not chat_id:
            return False

        profit_emoji = "📈" if summary.get("total_profit_loss", 0) >= 0 else "📉"
        message = (
            f"📊 *포트폴리오 일일 요약*\n\n"
            f"총 평가액: *${summary.get('total_value', 0):,.2f}*\n"
            f"총 투자금: ${summary.get('total_invested', 0):,.2f}\n"
            f"{profit_emoji} 수익/손실: ${summary.get('total_profit_loss', 0):+,.2f} "
            f"({summary.get('total_profit_loss_pct', 0):+.2f}%)\n"
            f"보유 코인: {summary.get('holding_count', 0)}개"
        )

        try:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="Markdown",
            )
            return True
        except Exception:
            return False

    async def check_and_notify_alerts(
        self,
        db,
        price_fetcher,
    ) -> int:
        """
        APScheduler에서 주기적으로 호출 - 모든 활성 알림 점검 후 발송
        반환값: 발송된 알림 수
        """
        from sqlalchemy import select
        from app.models.alert import PriceAlert
        from app.models.user import User
        from datetime import datetime

        # 활성 알림 전체 조회
        result = await db.execute(
            select(PriceAlert).where(
                PriceAlert.is_active == True,
                PriceAlert.is_triggered == False,
            )
        )
        alerts = result.scalars().all()

        if not alerts:
            return 0

        # 알림에 포함된 심볼 목록 추출 후 일괄 가격 조회
        symbols = list({alert.symbol for alert in alerts})
        prices = await price_fetcher.get_prices(symbols)

        notified_count = 0
        for alert in alerts:
            current_price = prices.get(alert.symbol)
            if current_price is None:
                continue

            # 목표가 도달 여부 확인
            triggered = (
                alert.direction == "above" and current_price >= alert.target_price
            ) or (
                alert.direction == "below" and current_price <= alert.target_price
            )

            if triggered:
                # 사용자 텔레그램 chat_id 조회
                user_result = await db.execute(
                    select(User).where(User.id == alert.user_id)
                )
                user = user_result.scalar_one_or_none()

                if user and user.telegram_chat_id:
                    sent = await self.send_price_alert(
                        chat_id=user.telegram_chat_id,
                        symbol=alert.symbol,
                        current_price=current_price,
                        target_price=alert.target_price,
                        direction=alert.direction,
                    )
                    if sent:
                        # 알림 발송 완료 처리
                        alert.is_triggered = True
                        alert.triggered_at = datetime.utcnow()
                        notified_count += 1

        await db.commit()
        return notified_count


# 전역 인스턴스
notifier = TelegramNotifier()

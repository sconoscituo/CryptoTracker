import httpx
from typing import Optional
from app.config import settings


class PriceAlertService:
    """
    CoinGecko API로 현재가 조회 + 알림 조건 체크 + 텔레그램 발송을 담당하는 서비스.
    기존 PriceFetcher / TelegramNotifier 와 독립적으로 동작하며,
    스케줄러 또는 라우터에서 직접 호출 가능하도록 설계.
    """

    COINGECKO_BASE = settings.coingecko_api_url

    async def get_current_price(self, coin_id: str) -> dict:
        """
        단일 코인의 USD / KRW 현재가 조회.
        반환 예: {"usd": 65432.1, "krw": 87654321.0}
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                r = await client.get(
                    f"{self.COINGECKO_BASE}/simple/price",
                    params={"ids": coin_id, "vs_currencies": "usd,krw"},
                )
                r.raise_for_status()
                data = r.json()
                return data.get(coin_id, {})
            except (httpx.HTTPError, KeyError):
                return {}

    async def get_current_prices_bulk(self, coin_ids: list[str]) -> dict[str, dict]:
        """
        여러 코인 일괄 USD / KRW 현재가 조회.
        반환 예: {"bitcoin": {"usd": 65432.1, "krw": 87654321.0}, ...}
        """
        ids_str = ",".join(coin_ids)
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                r = await client.get(
                    f"{self.COINGECKO_BASE}/simple/price",
                    params={"ids": ids_str, "vs_currencies": "usd,krw"},
                )
                r.raise_for_status()
                return r.json()
            except (httpx.HTTPError, KeyError):
                return {}

    async def check_alerts(self, db, telegram_token: Optional[str] = None) -> int:
        """
        DB의 활성 알림 전체 조회 → 현재가와 비교 → 조건 충족 시 텔레그램 발송.
        반환값: 발송된 알림 수.
        telegram_token 미지정 시 settings.telegram_bot_token 사용.
        """
        from sqlalchemy import select
        from app.models.alert import PriceAlert
        from app.models.user import User
        from datetime import datetime

        bot_token = telegram_token or settings.telegram_bot_token

        # 활성 & 미발송 알림 조회
        result = await db.execute(
            select(PriceAlert).where(
                PriceAlert.is_active == True,
                PriceAlert.is_triggered == False,
            )
        )
        alerts = result.scalars().all()

        if not alerts:
            return 0

        # 고유 심볼 추출 후 일괄 가격 조회
        symbols = list({alert.symbol for alert in alerts})
        prices_data = await self.get_current_prices_bulk(symbols)

        notified_count = 0
        for alert in alerts:
            coin_data = prices_data.get(alert.symbol, {})
            current_price = coin_data.get("usd")
            if current_price is None:
                continue

            triggered = (
                alert.direction == "above" and current_price >= alert.target_price
            ) or (
                alert.direction == "below" and current_price <= alert.target_price
            )

            if not triggered:
                continue

            # 사용자 텔레그램 chat_id 조회
            user_result = await db.execute(
                select(User).where(User.id == alert.user_id)
            )
            user = user_result.scalar_one_or_none()

            if user and user.telegram_chat_id and bot_token:
                sent = await send_telegram_alert(
                    bot_token=bot_token,
                    chat_id=user.telegram_chat_id,
                    message=_build_alert_message(
                        symbol=alert.symbol,
                        current_price=current_price,
                        current_krw=coin_data.get("krw"),
                        target_price=alert.target_price,
                        direction=alert.direction,
                    ),
                )
                if sent:
                    alert.is_triggered = True
                    alert.triggered_at = datetime.utcnow()
                    notified_count += 1

        await db.commit()
        return notified_count


def _build_alert_message(
    symbol: str,
    current_price: float,
    target_price: float,
    direction: str,
    current_krw: Optional[float] = None,
) -> str:
    """텔레그램 알림 메시지 포맷 구성"""
    direction_text = "이상 돌파" if direction == "above" else "이하 하락"
    symbol_upper = symbol.upper()
    krw_line = f"현재가 (KRW): *₩{current_krw:,.0f}*\n" if current_krw else ""
    return (
        f"🔔 *CryptoTracker 가격 알림*\n\n"
        f"코인: *{symbol_upper}*\n"
        f"현재가 (USD): *${current_price:,.4f}*\n"
        f"{krw_line}"
        f"목표가: ${target_price:,.4f} {direction_text}\n\n"
        f"설정하신 목표가에 도달했습니다\\!"
    )


async def send_telegram_alert(bot_token: str, chat_id: str, message: str) -> bool:
    """
    텔레그램 Bot API로 메시지 직접 발송 (python-telegram-bot 라이브러리 불필요).
    반환값: 발송 성공 여부
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.post(
                url,
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "MarkdownV2",
                },
            )
            return r.status_code == 200
        except httpx.HTTPError:
            return False


# 전역 인스턴스
price_alert_service = PriceAlertService()

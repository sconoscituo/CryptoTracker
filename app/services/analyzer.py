from datetime import datetime
from typing import Optional
import google.generativeai as genai
from app.config import settings


class MarketAnalyzer:
    """Gemini AI를 활용한 암호화폐 시장 분석"""

    def __init__(self):
        # Gemini AI 초기화
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

    async def analyze_market(
        self,
        symbol: str,
        coin_info: dict,
        fear_greed: Optional[dict] = None,
    ) -> dict:
        """
        Gemini AI로 특정 코인의 시장 심리 및 트렌드 분석
        - 공포/탐욕 지수 해석
        - 24h/7d 가격 변동 분석
        - 매수/홀드/매도 추천
        """
        if not self.model:
            return self._fallback_analysis(symbol, coin_info, fear_greed)

        # 프롬프트 구성
        fear_greed_text = ""
        if fear_greed:
            fear_greed_text = f"공포/탐욕 지수: {fear_greed['value']} ({fear_greed['classification']})"

        prompt = f"""
당신은 암호화폐 시장 분석 전문가입니다. 다음 데이터를 기반으로 분석해주세요.

## 코인 정보
- 코인: {coin_info.get('name')} ({symbol.upper()})
- 현재가: ${coin_info.get('current_price_usd', 'N/A'):,.2f}
- 24시간 변동률: {coin_info.get('price_change_24h_pct', 'N/A'):.2f}%
- 7일 변동률: {coin_info.get('price_change_7d_pct', 'N/A'):.2f}%
- 시가총액: ${coin_info.get('market_cap_usd', 0):,.0f}
- 24시간 거래량: ${coin_info.get('volume_24h', 0):,.0f}
- 역대 최고가(ATH): ${coin_info.get('ath_usd', 'N/A'):,.2f}
{fear_greed_text}

## 분석 요청
다음 항목을 간결하게 분석해주세요 (한국어로):

1. **시장 심리**: 현재 시장 분위기 (2-3문장)
2. **공포/탐욕 해석**: 지수가 의미하는 바 (1-2문장)
3. **트렌드 분석**: 단기 가격 움직임 해석 (2-3문장)
4. **투자 관점**: 매수/홀드/매도 관점에서의 판단 (2-3문장, 투자 권유 아님)

※ 이 분석은 정보 제공 목적이며 투자 권유가 아닙니다.
"""

        try:
            response = await self.model.generate_content_async(prompt)
            analysis_text = response.text

            # 응답 파싱
            return {
                "symbol": symbol,
                "current_price": coin_info.get("current_price_usd", 0),
                "fear_greed_interpretation": self._extract_section(analysis_text, "공포/탐욕 해석"),
                "market_sentiment": self._extract_section(analysis_text, "시장 심리"),
                "trend_analysis": self._extract_section(analysis_text, "트렌드 분석"),
                "recommendation": self._extract_section(analysis_text, "투자 관점"),
                "analysis_text": analysis_text,
                "analyzed_at": datetime.utcnow(),
            }
        except Exception:
            return self._fallback_analysis(symbol, coin_info, fear_greed)

    def _extract_section(self, text: str, section_name: str) -> str:
        """마크다운 응답에서 특정 섹션 추출"""
        lines = text.split("\n")
        capture = False
        result = []
        for line in lines:
            if section_name in line and "**" in line:
                capture = True
                continue
            if capture:
                if line.startswith("**") or line.startswith("#"):
                    break
                if line.strip():
                    result.append(line.strip())
        return " ".join(result) if result else "분석 정보를 가져올 수 없습니다."

    def _fallback_analysis(self, symbol: str, coin_info: dict, fear_greed: Optional[dict]) -> dict:
        """AI 키 미설정 시 기본 분석 반환"""
        price_change = coin_info.get("price_change_24h_pct", 0) or 0
        sentiment = "상승세" if price_change > 3 else "하락세" if price_change < -3 else "보합세"
        fg_text = f"공포/탐욕 지수 {fear_greed['value']}({fear_greed['classification']})" if fear_greed else "공포/탐욕 지수 데이터 없음"

        return {
            "symbol": symbol,
            "current_price": coin_info.get("current_price_usd", 0),
            "fear_greed_interpretation": fg_text,
            "market_sentiment": f"24시간 {price_change:.1f}% 변동, 현재 {sentiment}",
            "trend_analysis": "AI 분석을 사용하려면 GEMINI_API_KEY를 설정하세요.",
            "recommendation": "투자 결정은 본인 판단으로 하시기 바랍니다.",
            "analysis_text": "Gemini AI 키가 설정되지 않아 기본 분석만 제공됩니다.",
            "analyzed_at": datetime.utcnow(),
        }


# 전역 인스턴스
market_analyzer = MarketAnalyzer()

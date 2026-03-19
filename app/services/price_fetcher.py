import httpx
from typing import Optional
from app.config import settings


class PriceFetcher:
    """CoinGecko 무료 API로 암호화폐 가격 수집"""

    BASE_URL = settings.coingecko_api_url

    async def get_price(self, symbol: str, vs_currency: str = "usd") -> Optional[float]:
        """단일 코인 현재가 조회"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/simple/price",
                    params={"ids": symbol, "vs_currencies": vs_currency},
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get(symbol, {}).get(vs_currency)
            except (httpx.HTTPError, KeyError):
                return None

    async def get_prices(self, symbols: list[str], vs_currency: str = "usd") -> dict[str, float]:
        """여러 코인 현재가 일괄 조회"""
        ids = ",".join(symbols)
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/simple/price",
                    params={"ids": ids, "vs_currencies": vs_currency},
                )
                resp.raise_for_status()
                data = resp.json()
                # {symbol: price} 형태로 변환
                return {symbol: data[symbol][vs_currency] for symbol in symbols if symbol in data}
            except (httpx.HTTPError, KeyError):
                return {}

    async def get_coin_info(self, symbol: str) -> Optional[dict]:
        """코인 상세 정보 조회 (시가총액, 거래량, 24h 변동률 등)"""
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/coins/{symbol}",
                    params={
                        "localization": "false",
                        "tickers": "false",
                        "community_data": "false",
                        "developer_data": "false",
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                market_data = data.get("market_data", {})
                return {
                    "symbol": symbol,
                    "name": data.get("name"),
                    "current_price_usd": market_data.get("current_price", {}).get("usd"),
                    "market_cap_usd": market_data.get("market_cap", {}).get("usd"),
                    "volume_24h": market_data.get("total_volume", {}).get("usd"),
                    "price_change_24h_pct": market_data.get("price_change_percentage_24h"),
                    "price_change_7d_pct": market_data.get("price_change_percentage_7d"),
                    "ath_usd": market_data.get("ath", {}).get("usd"),
                    "atl_usd": market_data.get("atl", {}).get("usd"),
                }
            except (httpx.HTTPError, KeyError):
                return None

    async def get_fear_greed_index(self) -> Optional[dict]:
        """공포/탐욕 지수 조회 (alternative.me API)"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get("https://api.alternative.me/fng/")
                resp.raise_for_status()
                data = resp.json()
                item = data["data"][0]
                return {
                    "value": int(item["value"]),
                    "classification": item["value_classification"],  # "Fear", "Greed" 등
                }
            except (httpx.HTTPError, KeyError, IndexError):
                return None

    async def search_coin(self, query: str) -> list[dict]:
        """코인 검색 (이름 또는 심볼로)"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/search",
                    params={"query": query},
                )
                resp.raise_for_status()
                data = resp.json()
                # 상위 10개 결과만 반환
                return [
                    {"id": coin["id"], "name": coin["name"], "symbol": coin["symbol"]}
                    for coin in data.get("coins", [])[:10]
                ]
            except (httpx.HTTPError, KeyError):
                return []


# 전역 인스턴스
price_fetcher = PriceFetcher()

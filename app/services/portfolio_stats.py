"""포트폴리오 통계 계산"""
from datetime import datetime, timedelta

def calculate_roi(buy_price: float, current_price: float, quantity: float) -> dict:
    """투자 수익률 계산"""
    invested = buy_price * quantity
    current = current_price * quantity
    profit = current - invested
    roi_pct = (profit / invested * 100) if invested > 0 else 0
    return {
        "invested_krw": invested,
        "current_value_krw": current,
        "profit_krw": profit,
        "roi_percent": round(roi_pct, 2),
    }

def get_portfolio_summary(holdings: list[dict]) -> dict:
    """전체 포트폴리오 요약"""
    total_invested = sum(h["buy_price"] * h["quantity"] for h in holdings)
    total_current = sum(h["current_price"] * h["quantity"] for h in holdings)
    return {
        "total_invested": total_invested,
        "total_current": total_current,
        "total_profit": total_current - total_invested,
        "total_roi_percent": round((total_current - total_invested) / total_invested * 100, 2) if total_invested > 0 else 0,
        "holdings_count": len(holdings),
    }

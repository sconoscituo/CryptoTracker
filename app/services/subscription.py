from enum import Enum

class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"   # 월 7,900원

PLAN_LIMITS = {
    PlanType.FREE: {"portfolio_coins": 5,  "price_alerts": 3,  "ai_analysis": False, "fear_greed": True},
    PlanType.PRO:  {"portfolio_coins": 100,"price_alerts": 50, "ai_analysis": True,  "fear_greed": True},
}
PLAN_PRICES_KRW = {PlanType.FREE: 0, PlanType.PRO: 7900}

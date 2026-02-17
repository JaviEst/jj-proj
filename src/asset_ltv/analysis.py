from __future__ import annotations

from collections import deque
from datetime import timedelta
from typing import Deque

from .models import AnalysisResult, PricePoint


def moving_average_4y(prices: list[PricePoint]) -> float:
    """Time-based moving average using trailing 4 years from the latest date."""
    end_day = prices[-1].day
    start_day = end_day - timedelta(days=365 * 4)

    window: Deque[float] = deque()
    total = 0.0

    for point in prices:
        if point.day < start_day:
            continue
        window.append(point.price)
        total += point.price

    if not window:
        raise ValueError("Not enough data in trailing 4-year window")

    return total / len(window)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def analyze_ltv(
    asset: str,
    current_price: float,
    baseline_4y_ma: float,
    entry_ltv: float,
    liquidation_ltv: float,
    margin_call_ltv: float,
    safety_buffer: float,
) -> AnalysisResult:
    if current_price <= 0 or baseline_4y_ma <= 0:
        raise ValueError("Prices must be positive")
    if liquidation_ltv <= 0 or margin_call_ltv <= 0:
        raise ValueError("LTV thresholds must be positive")
    if margin_call_ltv >= liquidation_ltv:
        raise ValueError("Margin-call LTV must be below liquidation LTV")

    stress_ratio = current_price / baseline_4y_ma
    stressed_ltv = entry_ltv * stress_ratio

    max_for_margin = margin_call_ltv / stress_ratio
    max_for_liquidation = liquidation_ltv / stress_ratio

    conservative_margin = max(0.0, margin_call_ltv - safety_buffer)
    recommended = conservative_margin / stress_ratio
    recommended = clamp(recommended, 0.0, liquidation_ltv)

    return AnalysisResult(
        asset=asset,
        current_price=current_price,
        baseline_4y_ma=baseline_4y_ma,
        current_ltv=entry_ltv,
        stressed_ltv_at_baseline=stressed_ltv,
        max_entry_ltv_for_margin_call=max_for_margin,
        max_entry_ltv_for_liquidation=max_for_liquidation,
        recommended_max_entry_ltv=recommended,
    )


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"

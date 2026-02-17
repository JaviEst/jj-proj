from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .analysis import analyze_ltv, moving_average_4y
from .data.stooq import fetch_stooq_prices
from .models import AnalysisResult

SourceName = Literal["stooq"]


@dataclass(frozen=True)
class AnalysisEnvelope:
    source: SourceName
    symbol: str
    latest_price_date: str
    result: AnalysisResult


def run_live_analysis(
    *,
    asset: str,
    source: SourceName,
    symbol: str,
    entry_ltv: float,
    liquidation_ltv: float,
    margin_call_ltv: float,
    safety_buffer: float,
) -> AnalysisEnvelope:
    if margin_call_ltv >= liquidation_ltv:
        raise ValueError("margin_call_ltv must be lower than liquidation_ltv")

    if source != "stooq":
        raise ValueError(f"Unsupported source: {source}")

    prices = fetch_stooq_prices(symbol)
    current_price = prices[-1].price
    baseline_4y_ma = moving_average_4y(prices)

    result = analyze_ltv(
        asset=asset,
        current_price=current_price,
        baseline_4y_ma=baseline_4y_ma,
        entry_ltv=entry_ltv,
        liquidation_ltv=liquidation_ltv,
        margin_call_ltv=margin_call_ltv,
        safety_buffer=safety_buffer,
    )

    return AnalysisEnvelope(
        source=source,
        symbol=symbol,
        latest_price_date=prices[-1].day.isoformat(),
        result=result,
    )

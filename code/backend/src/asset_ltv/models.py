from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class PricePoint:
    day: date
    price: float


@dataclass(frozen=True)
class AnalysisResult:
    asset: str
    current_price: float
    baseline_4y_ma: float
    current_ltv: float
    stressed_ltv_at_baseline: float
    max_entry_ltv_for_margin_call: float
    max_entry_ltv_for_liquidation: float
    recommended_max_entry_ltv: float

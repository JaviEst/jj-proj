from __future__ import annotations

from prometheus_client import Gauge

from .service import AnalysisEnvelope

_LABELS = ("asset", "source", "symbol")

current_price_gauge = Gauge(
    "asset_ltv_current_price",
    "Latest observed asset price.",
    _LABELS,
)
baseline_4y_ma_gauge = Gauge(
    "asset_ltv_baseline_4y_ma",
    "Trailing 4-year moving average baseline.",
    _LABELS,
)
planned_entry_ltv_gauge = Gauge(
    "asset_ltv_planned_entry_ltv",
    "Planned entry LTV.",
    _LABELS,
)
stressed_ltv_gauge = Gauge(
    "asset_ltv_stressed_ltv_at_baseline",
    "LTV under stress to 4Y baseline.",
    _LABELS,
)
max_margin_ltv_gauge = Gauge(
    "asset_ltv_max_entry_ltv_for_margin_call",
    "Maximum entry LTV before margin call threshold is breached.",
    _LABELS,
)
max_liquidation_ltv_gauge = Gauge(
    "asset_ltv_max_entry_ltv_for_liquidation",
    "Maximum entry LTV before liquidation threshold is breached.",
    _LABELS,
)
recommended_ltv_gauge = Gauge(
    "asset_ltv_recommended_max_entry_ltv",
    "Conservative recommended max entry LTV.",
    _LABELS,
)


def record_analysis_metrics(envelope: AnalysisEnvelope) -> None:
    labels = {
        "asset": envelope.result.asset,
        "source": envelope.source,
        "symbol": envelope.symbol,
    }
    result = envelope.result

    current_price_gauge.labels(**labels).set(result.current_price)
    baseline_4y_ma_gauge.labels(**labels).set(result.baseline_4y_ma)
    planned_entry_ltv_gauge.labels(**labels).set(result.current_ltv)
    stressed_ltv_gauge.labels(**labels).set(result.stressed_ltv_at_baseline)
    max_margin_ltv_gauge.labels(**labels).set(result.max_entry_ltv_for_margin_call)
    max_liquidation_ltv_gauge.labels(**labels).set(result.max_entry_ltv_for_liquidation)
    recommended_ltv_gauge.labels(**labels).set(result.recommended_max_entry_ltv)

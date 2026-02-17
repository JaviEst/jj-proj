from __future__ import annotations

from datetime import date

import pytest

from asset_ltv.models import PricePoint
from asset_ltv.service import run_live_analysis

pytestmark = pytest.mark.integration


def test_run_live_analysis_integration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "asset_ltv.service.fetch_stooq_prices",
        lambda _symbol: [
            PricePoint(day=date(2023, 1, 1), price=20000.0),
            PricePoint(day=date(2024, 1, 1), price=30000.0),
            PricePoint(day=date(2025, 1, 1), price=40000.0),
            PricePoint(day=date(2026, 1, 1), price=50000.0),
        ],
    )

    envelope = run_live_analysis(
        asset="BTC",
        source="stooq",
        symbol="btcusd",
        entry_ltv=0.4,
        liquidation_ltv=0.8,
        margin_call_ltv=0.7,
        safety_buffer=0.05,
    )

    assert envelope.symbol == "btcusd"
    assert envelope.latest_price_date == "2026-01-01"
    assert envelope.result.current_price == 50000.0
    assert envelope.result.baseline_4y_ma > 0

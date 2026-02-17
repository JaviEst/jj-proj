from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from asset_ltv.api.main import app
from asset_ltv.models import AnalysisResult
from asset_ltv.service import AnalysisEnvelope

pytestmark = pytest.mark.pact

PACT_EXPECTATION = {
    "request": {
        "method": "POST",
        "path": "/v1/analyze",
        "body": {
            "asset": "BTC",
            "source": "stooq",
            "symbol": "btcusd",
            "entry_ltv": 0.5,
            "liquidation_ltv": 0.8,
            "margin_call_ltv": 0.7,
            "safety_buffer": 0.05,
        },
    },
    "response": {
        "status": 200,
        "required_fields": [
            "asset",
            "source",
            "symbol",
            "latest_price_date",
            "current_price",
            "baseline_4y_ma",
            "planned_entry_ltv",
            "stressed_ltv_at_baseline",
            "max_entry_ltv_for_margin_call",
            "max_entry_ltv_for_liquidation",
            "recommended_max_entry_ltv",
        ],
    },
}


def test_api_contract_pact(monkeypatch: pytest.MonkeyPatch) -> None:
    client = TestClient(app)
    envelope = AnalysisEnvelope(
        source="stooq",
        symbol="btcusd",
        latest_price_date="2026-01-01",
        result=AnalysisResult(
            asset="BTC",
            current_price=100000.0,
            baseline_4y_ma=80000.0,
            current_ltv=0.5,
            stressed_ltv_at_baseline=0.625,
            max_entry_ltv_for_margin_call=0.56,
            max_entry_ltv_for_liquidation=0.64,
            recommended_max_entry_ltv=0.52,
        ),
    )
    monkeypatch.setattr("asset_ltv.api.main.run_live_analysis", lambda **_kwargs: envelope)

    response = client.post(
        PACT_EXPECTATION["request"]["path"],
        json=PACT_EXPECTATION["request"]["body"],
    )

    assert response.status_code == PACT_EXPECTATION["response"]["status"]
    payload = response.json()["data"]
    for field in PACT_EXPECTATION["response"]["required_fields"]:
        assert field in payload

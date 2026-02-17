from datetime import date

from fastapi.testclient import TestClient

from asset_ltv.api.main import app
from asset_ltv.models import AnalysisResult
from asset_ltv.service import AnalysisEnvelope

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_sources_endpoint() -> None:
    response = client.get("/v1/sources")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload[0]["id"] == "stooq"


def test_analyze_endpoint_success(monkeypatch) -> None:
    envelope = AnalysisEnvelope(
        source="stooq",
        symbol="btcusd",
        latest_price_date=date(2026, 1, 1).isoformat(),
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
        "/v1/analyze",
        json={
            "asset": "BTC",
            "source": "stooq",
            "symbol": "btcusd",
            "entry_ltv": 0.5,
            "liquidation_ltv": 0.8,
            "margin_call_ltv": 0.7,
            "safety_buffer": 0.05,
        },
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["asset"] == "BTC"
    assert body["latest_price_date"] == "2026-01-01"
    assert body["recommended_max_entry_ltv"] == 0.52


def test_analyze_endpoint_value_error_to_400(monkeypatch) -> None:
    monkeypatch.setattr(
        "asset_ltv.api.main.run_live_analysis",
        lambda **_kwargs: (_ for _ in ()).throw(ValueError("invalid input")),
    )

    response = client.post(
        "/v1/analyze",
        json={
            "asset": "BTC",
            "source": "stooq",
            "symbol": "btcusd",
            "entry_ltv": 0.5,
            "liquidation_ltv": 0.8,
            "margin_call_ltv": 0.7,
            "safety_buffer": 0.05,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "invalid input"


def test_stream_analyze_endpoint_emits_event(monkeypatch) -> None:
    envelope = AnalysisEnvelope(
        source="stooq",
        symbol="btcusd",
        latest_price_date=date(2026, 1, 1).isoformat(),
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

    response = client.get(
        "/v1/stream/analyze",
        params={
            "asset": "BTC",
            "source": "stooq",
            "symbol": "btcusd",
            "entry_ltv": 0.5,
            "liquidation_ltv": 0.8,
            "margin_call_ltv": 0.7,
            "safety_buffer": 0.05,
            "interval_seconds": 1,
            "max_updates": 1,
        },
    )

    assert response.status_code == 200
    assert "event: analysis" in response.text

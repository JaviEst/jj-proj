from datetime import date

import pytest
from click.testing import CliRunner

from app import cli as app_cli
from asset_ltv.analysis import analyze_ltv, moving_average_4y
from asset_ltv.cli import cli
from asset_ltv.data.stooq import fetch_stooq_prices, load_prices_from_rows
from asset_ltv.models import PricePoint


def test_moving_average_4y_filters_old_points() -> None:
    prices = [
        PricePoint(day=date(2020, 1, 1), price=100.0),
        PricePoint(day=date(2022, 1, 1), price=200.0),
        PricePoint(day=date(2024, 1, 1), price=300.0),
    ]

    # Latest date is 2024-01-01, so 2020-01-01 is outside trailing 4 years.
    assert moving_average_4y(prices) == pytest.approx(250.0)


def test_analyze_ltv_recommended_is_below_margin_threshold() -> None:
    result = analyze_ltv(
        asset="BTC",
        current_price=100000.0,
        baseline_4y_ma=50000.0,
        entry_ltv=0.40,
        liquidation_ltv=0.80,
        margin_call_ltv=0.70,
        safety_buffer=0.05,
    )

    assert result.stressed_ltv_at_baseline == pytest.approx(0.80)
    assert result.max_entry_ltv_for_margin_call == pytest.approx(0.35)
    assert result.recommended_max_entry_ltv == pytest.approx(0.325)


def test_load_prices_from_rows_accepts_stooq_headers() -> None:
    rows = [
        {"Date": "2025-01-01", "Close": "10.0"},
        {"Date": "2025-01-02", "Close": "12.0"},
    ]

    prices = load_prices_from_rows(rows)

    assert len(prices) == 2
    assert prices[1].price == 12.0


def test_fetch_stooq_prices_parses_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = "Date,Open,High,Low,Close,Volume\n2025-01-01,1,1,1,10,1\n2025-01-02,1,1,1,11,1\n"

    class DummyResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return payload.encode("utf-8")

    monkeypatch.setattr("asset_ltv.data.stooq.urlopen", lambda *_args, **_kwargs: DummyResponse())

    prices = fetch_stooq_prices("btcusd")

    assert prices[0].day == date(2025, 1, 1)
    assert prices[0].price == 10.0


def test_cli_runs_with_live_source(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "asset_ltv.cli.fetch_stooq_prices",
        lambda _symbol: [
            PricePoint(day=date(2025, 1, 1), price=100.0),
            PricePoint(day=date(2026, 1, 1), price=120.0),
        ],
    )
    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            "--asset",
            "BTC",
            "--symbol",
            "btcusd",
            "--entry-ltv",
            "0.4",
        ],
    )

    assert result.exit_code == 0
    assert "Asset" in result.output
    assert "BTC" in result.output
    assert "Price Date" in result.output
    assert "2026-01-01" in result.output


def test_cli_rejects_invalid_thresholds() -> None:
    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            "--asset",
            "BTC",
            "--symbol",
            "btcusd",
            "--margin-call-ltv",
            "0.8",
            "--liquidation-ltv",
            "0.8",
        ],
    )

    assert result.exit_code != 0
    assert "--margin-call-ltv" in result.output


def test_app_entrypoint_uses_package_cli() -> None:
    assert app_cli is cli

from __future__ import annotations

import click

from .analysis import analyze_ltv, moving_average_4y, pct
from .data.stooq import fetch_stooq_prices


def render_report(
    *,
    asset: str,
    price_date: str,
    current_price: float,
    baseline_4y_ma: float,
    planned_entry_ltv: str,
    stressed_ltv: str,
    max_for_margin: str,
    max_for_liquidation: str,
    recommended_max: str,
    margin_target: str,
    liquidation_target: str,
    buffer: str,
) -> str:
    rows = [
        ("Asset", asset),
        ("Price Date", price_date),
        ("Current Price", f"{current_price:.4f}"),
        ("4Y MA Baseline", f"{baseline_4y_ma:.4f}"),
        ("Planned Entry LTV", planned_entry_ltv),
        ("Stressed LTV @ 4Y MA", stressed_ltv),
        (f"Max Entry LTV (< {margin_target} margin call)", max_for_margin),
        (f"Max Entry LTV (< {liquidation_target} liquidation)", max_for_liquidation),
        (f"Recommended Max Entry LTV ({buffer} buffer)", recommended_max),
    ]

    width = max(len(label) for label, _ in rows)
    header = "LTV Stress Analysis"
    divider = "-" * (width + 22)
    lines = [header, divider]
    lines.extend(f"{label:<{width}} : {value}" for label, value in rows)
    return "\n".join(lines)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--asset", required=True, type=str, help="Asset ticker/name for reporting.")
@click.option(
    "--source",
    type=click.Choice(["stooq"], case_sensitive=False),
    default="stooq",
    show_default=True,
    help="Live data source.",
)
@click.option(
    "--symbol",
    required=True,
    type=str,
    help="Live source symbol. Example: btcusd, aapl.us.",
)
@click.option(
    "--entry-ltv",
    type=click.FloatRange(min=0.0, min_open=True, max=1.0),
    default=0.50,
    show_default=True,
    help="Planned entry LTV as decimal.",
)
@click.option(
    "--liquidation-ltv",
    type=click.FloatRange(min=0.0, min_open=True, max=1.0),
    default=0.80,
    show_default=True,
    help="Liquidation threshold LTV as decimal.",
)
@click.option(
    "--margin-call-ltv",
    type=click.FloatRange(min=0.0, min_open=True, max=1.0),
    default=0.70,
    show_default=True,
    help="Margin-call threshold LTV as decimal.",
)
@click.option(
    "--safety-buffer",
    type=click.FloatRange(min=0.0, max=1.0),
    default=0.05,
    show_default=True,
    help="Extra room below margin-call threshold.",
)
def cli(
    asset: str,
    source: str,
    symbol: str,
    entry_ltv: float,
    liquidation_ltv: float,
    margin_call_ltv: float,
    safety_buffer: float,
) -> None:
    """Estimate safe entry LTV using a 4-year moving-average baseline and live prices."""
    if margin_call_ltv >= liquidation_ltv:
        raise click.BadParameter(
            "must be lower than --liquidation-ltv", param_hint="--margin-call-ltv"
        )

    try:
        if source.lower() == "stooq":
            prices = fetch_stooq_prices(symbol)
        else:
            raise click.ClickException(f"Unsupported source: {source}")
    except (RuntimeError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc

    try:
        current_price = prices[-1].price
        baseline_4y_ma = moving_average_4y(prices)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    result = analyze_ltv(
        asset=asset,
        current_price=current_price,
        baseline_4y_ma=baseline_4y_ma,
        entry_ltv=entry_ltv,
        liquidation_ltv=liquidation_ltv,
        margin_call_ltv=margin_call_ltv,
        safety_buffer=safety_buffer,
    )

    report = render_report(
        asset=result.asset,
        price_date=prices[-1].day.isoformat(),
        current_price=result.current_price,
        baseline_4y_ma=result.baseline_4y_ma,
        planned_entry_ltv=pct(result.current_ltv),
        stressed_ltv=pct(result.stressed_ltv_at_baseline),
        max_for_margin=pct(result.max_entry_ltv_for_margin_call),
        max_for_liquidation=pct(result.max_entry_ltv_for_liquidation),
        recommended_max=pct(result.recommended_max_entry_ltv),
        margin_target=pct(margin_call_ltv),
        liquidation_target=pct(liquidation_ltv),
        buffer=pct(safety_buffer),
    )
    click.echo(report)

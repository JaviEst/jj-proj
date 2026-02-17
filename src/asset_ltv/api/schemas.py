from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok"] = Field(description="Service health status.")


class SourceDefinition(BaseModel):
    id: Literal["stooq"] = Field(description="Internal source identifier.")
    name: str = Field(description="Display name for UI selection.")
    supports_daily_prices: bool = Field(description="Whether daily candles are supported.")


class AnalyzeRequest(BaseModel):
    asset: str = Field(description="Display asset name used in reports.", examples=["BTC"])
    source: Literal["stooq"] = Field(description="Live market data source identifier.")
    symbol: str = Field(description="Symbol as expected by source.", examples=["btcusd"])
    entry_ltv: float = Field(
        gt=0,
        le=1,
        description="Planned entry LTV as decimal between 0 and 1.",
        examples=[0.5],
    )
    liquidation_ltv: float = Field(
        gt=0,
        le=1,
        description="Liquidation threshold LTV as decimal between 0 and 1.",
        examples=[0.8],
    )
    margin_call_ltv: float = Field(
        gt=0,
        le=1,
        description="Margin-call threshold LTV as decimal between 0 and 1.",
        examples=[0.7],
    )
    safety_buffer: float = Field(
        ge=0,
        le=1,
        description="Safety margin subtracted from margin-call threshold.",
        examples=[0.05],
    )


class AnalysisData(BaseModel):
    asset: str = Field(description="Asset display name.")
    source: Literal["stooq"] = Field(description="Data source used for analysis.")
    symbol: str = Field(description="Source symbol that was queried.")
    latest_price_date: str = Field(description="Latest price date in ISO-8601 format.")
    current_price: float = Field(description="Most recent price returned by source.")
    baseline_4y_ma: float = Field(description="Trailing 4-year moving average baseline.")
    planned_entry_ltv: float = Field(description="Requested entry LTV.")
    stressed_ltv_at_baseline: float = Field(description="LTV after stress to 4Y baseline.")
    max_entry_ltv_for_margin_call: float = Field(
        description="Maximum entry LTV to stay below margin-call threshold."
    )
    max_entry_ltv_for_liquidation: float = Field(
        description="Maximum entry LTV to stay below liquidation threshold."
    )
    recommended_max_entry_ltv: float = Field(
        description="Conservative entry LTV using safety buffer."
    )


class AnalyzeResponse(BaseModel):
    data: AnalysisData


class ErrorResponse(BaseModel):
    detail: str = Field(description="Human-readable error message.")

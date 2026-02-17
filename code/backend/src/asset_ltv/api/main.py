from __future__ import annotations

import asyncio
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from ..metrics import record_analysis_metrics
from ..service import AnalysisEnvelope, SourceName, run_live_analysis
from .schemas import (
    AnalysisData,
    AnalyzeRequest,
    AnalyzeResponse,
    ErrorResponse,
    HealthResponse,
    SourceDefinition,
)

app = FastAPI(
    title="Asset LTV API",
    description=("REST API for asset LTV stress analysis using a 4-year moving average baseline."),
    version="0.1.0",
)

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:4200")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _to_analyze_response(envelope: AnalysisEnvelope) -> AnalyzeResponse:
    result = envelope.result
    return AnalyzeResponse(
        data=AnalysisData(
            asset=result.asset,
            source=envelope.source,
            symbol=envelope.symbol,
            latest_price_date=envelope.latest_price_date,
            current_price=result.current_price,
            baseline_4y_ma=result.baseline_4y_ma,
            planned_entry_ltv=result.current_ltv,
            stressed_ltv_at_baseline=result.stressed_ltv_at_baseline,
            max_entry_ltv_for_margin_call=result.max_entry_ltv_for_margin_call,
            max_entry_ltv_for_liquidation=result.max_entry_ltv_for_liquidation,
            recommended_max_entry_ltv=result.recommended_max_entry_ltv,
        )
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["system"],
)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get(
    "/metrics",
    summary="Prometheus metrics",
    tags=["system"],
)
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get(
    "/v1/sources",
    response_model=list[SourceDefinition],
    summary="List supported market data sources",
    tags=["metadata"],
)
def list_sources() -> list[SourceDefinition]:
    return [
        SourceDefinition(
            id="stooq",
            name="Stooq",
            supports_daily_prices=True,
        )
    ]


@app.post(
    "/v1/analyze",
    response_model=AnalyzeResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Invalid request parameters or unsupported source.",
        },
        status.HTTP_502_BAD_GATEWAY: {
            "model": ErrorResponse,
            "description": "Failed to retrieve data from external source.",
        },
    },
    summary="Run live LTV stress analysis",
    tags=["analysis"],
)
def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    try:
        envelope = run_live_analysis(
            asset=payload.asset,
            source=payload.source,
            symbol=payload.symbol,
            entry_ltv=payload.entry_ltv,
            liquidation_ltv=payload.liquidation_ltv,
            margin_call_ltv=payload.margin_call_ltv,
            safety_buffer=payload.safety_buffer,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    record_analysis_metrics(envelope)
    return _to_analyze_response(envelope)


@app.get(
    "/v1/stream/analyze",
    summary="Stream live LTV stress analysis updates",
    tags=["analysis"],
)
async def stream_analyze(
    asset: str = Query(description="Display asset name used in reports."),
    source: SourceName = Query(default="stooq", description="Live market data source identifier."),
    symbol: str = Query(description="Symbol as expected by source."),
    entry_ltv: float = Query(default=0.5, gt=0, le=1),
    liquidation_ltv: float = Query(default=0.8, gt=0, le=1),
    margin_call_ltv: float = Query(default=0.7, gt=0, le=1),
    safety_buffer: float = Query(default=0.05, ge=0, le=1),
    interval_seconds: float = Query(default=5.0, ge=1.0, le=60.0),
    max_updates: int = Query(default=0, ge=0, le=10000),
) -> StreamingResponse:
    async def event_stream():
        sent = 0
        while max_updates == 0 or sent < max_updates:
            try:
                envelope = run_live_analysis(
                    asset=asset,
                    source=source,
                    symbol=symbol,
                    entry_ltv=entry_ltv,
                    liquidation_ltv=liquidation_ltv,
                    margin_call_ltv=margin_call_ltv,
                    safety_buffer=safety_buffer,
                )
                record_analysis_metrics(envelope)
                payload = _to_analyze_response(envelope).model_dump_json()
                yield f"event: analysis\ndata: {payload}\n\n"
            except (ValueError, RuntimeError) as exc:
                error_payload = ErrorResponse(detail=str(exc)).model_dump_json()
                yield f"event: error\ndata: {error_payload}\n\n"

            sent += 1
            if max_updates and sent >= max_updates:
                break
            await asyncio.sleep(interval_seconds)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


static_dir = Path(os.getenv("STATIC_DIR", "/app/static"))
if static_dir.exists():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")

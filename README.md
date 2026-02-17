# Asset LTV Service

Service to estimate safer entry loan-to-value (LTV) using a 4-year moving average as a stress baseline.

## Features

- Live price fetch from Stooq source.
- `click`-based CLI with typed option validation and helpful errors.
- FastAPI backend with OpenAPI/Swagger docs for frontend integration.
- Compute trailing 4-year moving average from latest price date.
- Estimate stressed LTV if price reverts to that baseline.
- Report:
  - max entry LTV under margin-call threshold (default `70%`)
  - max entry LTV under liquidation threshold (default `80%`)
  - conservative recommended max entry LTV (margin-call minus safety buffer)

## Formula

- `L_stress = L_entry * (P_now / P_base)`
- To stay below threshold `T`: `L_entry <= T / (P_now / P_base)`

## App usage

CLI (live Stooq):

```bash
uv run --with-requirements requirements-test.txt python -m asset_ltv --asset BTC --source stooq --symbol btcusd --entry-ltv 0.50
```

API server:

```bash
uv run --with-requirements requirements-test.txt uvicorn asset_ltv.api.main:app --reload
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

Main endpoints:

- `GET /health`
- `GET /metrics` (Prometheus scrape endpoint)
- `GET /v1/sources`
- `POST /v1/analyze`
- `GET /v1/stream/analyze` (SSE push updates)

Example API request:

```json
{
  "asset": "BTC",
  "source": "stooq",
  "symbol": "btcusd",
  "entry_ltv": 0.5,
  "liquidation_ltv": 0.8,
  "margin_call_ltv": 0.7,
  "safety_buffer": 0.05
}
```

Legacy CLI examples:

Live Stooq:

```bash
uv run --with-requirements requirements-test.txt python -m asset_ltv --asset BTC --source stooq --symbol btcusd --entry-ltv 0.50
```

For equities (example):

```bash
uv run --with-requirements requirements-test.txt python -m asset_ltv --asset AAPL --source stooq --symbol aapl.us --entry-ltv 0.45
```

Show help:

```bash
uv run --with-requirements requirements-test.txt python -m asset_ltv --help
```

`app.py` remains as a compatibility wrapper and delegates to `asset_ltv.cli`.

## Project layout

```text
src/asset_ltv/
  cli.py            # CLI entry point + output rendering
  analysis.py       # pure business logic and LTV math
  service.py        # orchestration layer used by CLI/API
  models.py         # domain models (PricePoint, AnalysisResult)
  data/stooq.py     # data-access layer for live price fetching
  api/main.py       # FastAPI app + routes
  api/schemas.py    # request/response contracts for docs
```

## Docker

Backend image:

```bash
docker build -f Dockerfile.backend -t asset-ltv-backend .
```

Frontend image (expects Angular app under `frontend/`):

```bash
docker build -f Dockerfile.frontend -t asset-ltv-frontend .
```

Fullstack image (build Angular + serve API/static together):

```bash
docker build -f Dockerfile.fullstack -t asset-ltv-fullstack .
```

Docker Compose (full stack):

```bash
docker compose up --build
```

Docker Compose debug mode (API + UI auto-refresh on save):

```bash
docker compose -f docker-compose.yml -f docker-compose.debug.yml up --build
```

Debug URLs:
- UI dev server: `http://localhost:4200`
- API: `http://localhost:8000`
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`

In debug mode:
- API reloads automatically via `uvicorn --reload` when files in `src/` change.
- UI rebuilds on `frontend/build.mjs` changes and BrowserSync auto-refreshes the browser.

Open:

```text
UI: http://localhost:8000
Grafana: http://localhost:3000
Prometheus: http://localhost:9090
```

The dashboard supports:
- `once`: one-time request
- `pull`: client polling with interval
- `push`: server-sent events stream from `/v1/stream/analyze`

Ticker workflow:
- Enter any ticker (examples: `AAPL`, `TSLA`, `BTC`)
- Choose market (`US Equities`, `Crypto`, or `Raw Symbol`)
- Click `Apply Ticker` to auto-map source symbol (`AAPL` -> `aapl.us`, `BTC` -> `btcusd`)

Grafana graphs:
- Embedded directly in the UI
- Hover any line to inspect timestamp and value details
- Dashboard automatically filters by the active symbol

CI/local Docker build verification:

```bash
tox -e docker-build
```

## Developer setup

Install tooling with `uv`:

```bash
uv run --with-requirements requirements-test.txt pytest
uv run --with-requirements requirements-test.txt ruff check .
uv run --with-requirements requirements-test.txt ruff format --check .
```

Run all checks through tox:

```bash
tox -e format
tox -e lint
tox -e py
tox -e integration
tox -e pact
tox -e e2e-backend
```

Frontend E2E (Playwright):

```bash
npm --prefix frontend ci
npx --yes playwright@1.52.0 install --with-deps chromium
npx --yes playwright@1.52.0 test -c frontend/playwright.config.mjs
```

## Requirements split

- `requirements.txt`: runtime dependencies
- `requirements-test.txt`: test and quality tooling (`pytest`, `ruff`, `tox`)

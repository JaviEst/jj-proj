# Asset LTV Service

Service to estimate safer entry loan-to-value (LTV) using a 4-year moving average as a stress baseline.

## Features

- Live price fetch from Stooq source.
- `click`-based CLI with typed option validation.
- FastAPI backend with OpenAPI/Swagger docs.
- Frontend dashboard with pull/push live modes.
- Prometheus metrics and Grafana dashboard integration.

## Repository Structure

```text
code/
  backend/
    src/asset_ltv/
    tests/
    pyproject.toml
    tox.ini
    requirements.txt
    requirements-test.txt
  frontend/
    frontend/
      build.mjs
      package.json
      playwright.config.mjs
      tests/
.github/workflows/
  backend-ci.yml
  frontend-ci.yml
Dockerfile.fullstack
docker-compose.yml
docker-compose.debug.yml
MIGRATION_MATRIX.md
grafana/
prometheus/
```

## Quickstart

Backend CLI:

```bash
cd code/backend
uv run --with-requirements requirements-test.txt python -m asset_ltv --asset BTC --source stooq --symbol btcusd --entry-ltv 0.50
```

Backend API (local):

```bash
cd code/backend
uv run --with-requirements requirements-test.txt uvicorn asset_ltv.api.main:app --reload
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

## Docker

Build backend image:

```bash
docker build -f code/backend/Dockerfile.backend -t asset-ltv-backend .
```

Build frontend image:

```bash
docker build -f code/frontend/Dockerfile.frontend -t asset-ltv-frontend .
```

Build fullstack image:

```bash
docker build -f Dockerfile.fullstack -t asset-ltv-fullstack .
```

Run full stack:

```bash
docker compose up --build
```

Run debug stack (hot reload API/UI):

```bash
docker compose -f docker-compose.yml -f docker-compose.debug.yml up --build
```

Access points:

- UI/API combined app: `http://localhost:8000`
- UI dev server (debug mode): `http://localhost:4200`
- API docs: `http://localhost:8000/docs`
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`

## Testing and Quality

Backend (tox):

```bash
cd code/backend
tox -e format
tox -e lint
tox -e py
tox -e integration
tox -e pact
tox -e e2e-backend
```

Docker build validation through tox:

```bash
cd code/backend
tox -e docker-build
```

Frontend E2E:

```bash
npm --prefix code/frontend/frontend ci
npx --yes playwright@1.52.0 install --with-deps chromium
npx --yes playwright@1.52.0 test -c code/frontend/frontend/playwright.config.mjs
```

## CI Architecture

### Backend CI (`.github/workflows/backend-ci.yml`)

Jobs:
- Lint/format: Ruff checks via tox.
- Tests: unit + integration + pact + backend e2e, with coverage threshold.
- Security: gitleaks, pip-audit, semgrep.
- Containers: backend and fullstack Docker builds.
- Publish (optional): pushes backend/fullstack images to GHCR on `main` when enabled.

### Frontend CI (`.github/workflows/frontend-ci.yml`)

Jobs:
- Lint/build/test: npm lint/typecheck/build/unit (if scripts are configured).
- E2E: Playwright tests with artifact upload.
- Security/quality: hadolint + semgrep.
- Containers: frontend and fullstack Docker builds.
- Publish (optional): pushes frontend image to GHCR on `main` when enabled.

### Required/Optional Secrets and Variables

- Uses built-in `GITHUB_TOKEN` for checkout/scans/package pushes.
- Optional repository variable: `PUBLISH_DOCKER_IMAGES=true` to enable image publish jobs.

### Failure Triage

- Lint/format failures: run local tox and fix formatting/import/lint issues.
- Test failures: reproduce in `code/backend` or frontend Playwright command.
- Security failures: review scanner output and patch vulnerable patterns/dependencies.
- Docker build failures: rebuild specific Dockerfile locally with the same command from CI.

## Migration Notes

- Legacy `src/` moved to `code/backend/src/`.
- Legacy `tests/` moved to `code/backend/tests/`.
- Legacy `frontend/` moved to `code/frontend/frontend/`.
- Legacy `Dockerfile.backend` moved to `code/backend/Dockerfile.backend`.
- Legacy `Dockerfile.frontend` moved to `code/frontend/Dockerfile.frontend`.
- See `MIGRATION_MATRIX.md` for the full mapping.

# Migration Matrix

This matrix tracks the repository reshape from the legacy flat layout to the new split layout.

## Directory Moves

| Legacy Path | New Path | Notes |
|---|---|---|
| `src/` | `code/backend/src/` | Backend package source |
| `tests/` | `code/backend/tests/` | Backend test suites (unit/integration/e2e/pact) |
| `app.py` | `code/backend/app.py` | Backward-compatible Python entry wrapper |
| `pyproject.toml` | `code/backend/pyproject.toml` | Backend packaging and tool config |
| `tox.ini` | `code/backend/tox.ini` | Backend quality and test orchestration |
| `requirements.txt` | `code/backend/requirements.txt` | Backend runtime deps |
| `requirements-test.txt` | `code/backend/requirements-test.txt` | Backend test/lint deps |
| `sample_prices.csv` | `code/backend/sample_prices.csv` | Legacy sample data (retained) |
| `frontend/` | `code/frontend/frontend/` | Frontend source and tests |
| `Dockerfile.backend` | `code/backend/Dockerfile.backend` | Backend container build file |
| `Dockerfile.frontend` | `code/frontend/Dockerfile.frontend` | Frontend container build file |

## Retained Root Paths

| Path | Reason |
|---|---|
| `Dockerfile.fullstack` | Full-stack container build (backend + static frontend) |
| `docker-compose.yml` | Shared runtime stack orchestration |
| `docker-compose.debug.yml` | Local debug/hot-reload override |
| `.github/workflows/` | CI/CD workflows |
| `grafana/`, `prometheus/` | Observability provisioning/config |
| `README.md` | Project onboarding and operational docs |

## Path-Dependent Files Updated

- `.github/workflows/backend-ci.yml`
- `.github/workflows/frontend-ci.yml`
- `Dockerfile.fullstack`
- `docker-compose.yml`
- `docker-compose.debug.yml`
- `code/backend/tox.ini`
- `code/backend/pyproject.toml` (validated for new location)
- `code/frontend/frontend/playwright.config.mjs`
- `README.md`
- `.gitignore`

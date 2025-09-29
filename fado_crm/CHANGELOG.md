# Changelog

## v1.1.0 - Performance Monitoring and CI

Released: Draft (to be finalized after merging PRs)

### Added
- Performance monitoring endpoints under `/performance`:
  - `GET /performance/health` (public)
  - `GET /performance/metrics` (public, Prometheus format)
  - `GET /performance/database/stats` (admin)
  - `GET /performance/database/indexes` (admin)
  - `GET /performance/database/slow-queries` (admin)
  - `GET /performance/database/optimize` (admin)
  - `POST /performance/cache/clear` (admin)
- Prometheus + Grafana stack via `docker-compose` with default scrape for backend metrics
- Locust load tests and nightly workflow (`.github/workflows/loadtest-nightly.yml`)
- CI workflows:
  - `tests.yml` (pytest) — required check
  - `lint.yml` (black, isort, flake8)
  - `typecheck.yml` (mypy, non-blocking)
- API docs updated: Performance Monitoring section

### Changed
- Default `DATABASE_URL` alignment; import resilience; SQLAlchemy 2 compatibility
- Tests added for health/stats/indexes/metrics (4 passed locally)

### Notes
- Branch protection enabled on `main` (requires 1 approval + `tests` check)
- To run monitoring stack locally:
  ```bash
  cd fado_crm
  docker-compose up -d postgres redis backend prometheus grafana
  # Prometheus: http://localhost:9090
  # Grafana:    http://localhost:3001 (admin/admin)
  ```

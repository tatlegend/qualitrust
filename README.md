# QualiTrust Global — Qualification Verification System

A reference implementation for the MIM736 practical assignment: a DevOps-enabled
qualification verification system built with Flask + SQLite, tested with pytest,
linted with flake8, containerised with Docker, and wired into a GitHub Actions
CI/CD pipeline.

## The four core capabilities
1. **Register** — `POST /api/qualifications`
2. **Search** — `GET /api/qualifications?q=<term>` (fuzzy match)
3. **Retrieve** — `GET /api/qualifications/<certificate_number>` (exact match, full record)
4. **Verify** — `GET /api/verify/<certificate_number>` (VERIFIED / REVOKED / NOT_FOUND)

Every one of the above writes an entry to `audit_log`, giving a full auditable
trail of verification activity, viewable via `GET /api/audit-log`.

## Quick start (macOS)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python3 wsgi.py
```
Then open http://127.0.0.1:5000

## Running tests
```bash
PYTHONPATH=. pytest tests/ -v --cov=app --cov-report=term-missing
```
23 tests, 97% coverage as of the last run.

## Linting
```bash
flake8 app/ tests/ --max-line-length=100
```

## Docker (macOS — Apple Silicon and Intel both supported)
```bash
docker build -t qualitrust:latest .
docker run -d -p 5000:5000 qualitrust:latest
```

## CI/CD
See `.github/workflows/ci-cd.yml` — runs build, lint, test+coverage gate,
and a Docker build/smoke-test on every push and pull request.

## Architecture
- `app/routes.py` — thin HTTP layer (Flask blueprint)
- `app/verification.py` — framework-independent business rules (unit-tested in isolation)
- `app/db.py` — SQLite data access + audit logging
- `tests/test_verification_unit.py` — unit tests
- `tests/test_api_integration.py` — integration tests against the real API + DB

## Full guide
See the accompanying document: MIM736_QualiTrust_Practical_Guide.docx

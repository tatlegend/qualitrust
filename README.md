# QualiTrust Global — Qualification Verification System

A reference implementation for the MIM736 practical assignment: a DevOps-enabled
qualification verification system built with Flask + SQLite, tested with pytest,
linted with flake8, containerised with Docker, and wired into a GitHub Actions
CI/CD pipeline.

## Features
- Register a qualification/certification
- Search qualification records
- Verify the authenticity of a qualification by certificate number
- Revoke a qualification
- Auditable history of every action (audit_log table)

## Quick start
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
PYTHONPATH=. python wsgi.py
```
Then open http://127.0.0.1:5000

## Running tests
```bash
PYTHONPATH=. pytest tests/ -v --cov=app --cov-report=term-missing
```
19 tests, 98% coverage as of the last run.

## Linting
```bash
flake8 app/ tests/ --max-line-length=100
```

## Docker
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

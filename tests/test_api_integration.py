"""
Integration tests: exercise the Flask routes end-to-end against a real
(temporary) SQLite database. This is the 'Integration tests' evidence
required by the assignment's QA section.
"""
import json


SAMPLE = {
    "holder_name": "Chipo Ncube",
    "qualification_title": "MSc Computer Science",
    "institution": "Midlands State University",
    "issue_date": "2021-06-30",
    "certificate_number": "MSU-2021-004532",
}


def test_register_and_verify_flow(client):
    # Register
    resp = client.post("/api/qualifications", json=SAMPLE)
    assert resp.status_code == 201

    # Verify
    resp = client.get(f"/api/verify/{SAMPLE['certificate_number']}")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["result"] == "VERIFIED"


def test_verify_unknown_certificate_returns_not_found(client):
    resp = client.get("/api/verify/UNKNOWN-0000-0000")
    data = resp.get_json()
    assert data["result"] == "NOT_FOUND"


def test_duplicate_registration_rejected(client):
    client.post("/api/qualifications", json=SAMPLE)
    resp = client.post("/api/qualifications", json=SAMPLE)
    assert resp.status_code == 409


def test_search_finds_registered_qualification(client):
    client.post("/api/qualifications", json=SAMPLE)
    resp = client.get("/api/qualifications?q=Chipo")
    results = resp.get_json()
    assert len(results) == 1
    assert results[0]["certificate_number"] == SAMPLE["certificate_number"]


def test_revoke_then_verify_shows_revoked(client):
    client.post("/api/qualifications", json=SAMPLE)
    client.post(f"/api/qualifications/{SAMPLE['certificate_number']}/revoke")
    resp = client.get(f"/api/verify/{SAMPLE['certificate_number']}")
    assert resp.get_json()["result"] == "REVOKED"


def test_audit_log_records_actions(client):
    client.post("/api/qualifications", json=SAMPLE)
    client.get(f"/api/verify/{SAMPLE['certificate_number']}")
    resp = client.get("/api/audit-log")
    log = resp.get_json()
    actions = [entry["action"] for entry in log]
    assert "REGISTER" in actions
    assert "VERIFY" in actions


def test_invalid_payload_returns_400(client):
    bad_payload = dict(SAMPLE)
    bad_payload["certificate_number"] = "not-valid"
    resp = client.post("/api/qualifications", json=bad_payload)
    assert resp.status_code == 400

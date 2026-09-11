"""
Integration tests: exercise the Flask routes end-to-end against a real
(temporary) SQLite database. This is the 'Integration tests' evidence
required by the assignment's QA section.
"""
SAMPLE = {
    "holder_name": "Chipo Ncube",
    "qualification_title": "MSc Computer Science",
    "institution": "Midlands State University",
    "issue_date": "2021-06-30",
    "certificate_number": "MSU-2021-004532",
}


def test_about_and_contact_pages_render(client):
    about_resp = client.get("/about")
    contact_resp = client.get("/contact")

    assert about_resp.status_code == 200
    assert b"About Us" in about_resp.data
    assert contact_resp.status_code == 200
    assert b"Contact Us" in contact_resp.data


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


def test_retrieve_existing_record_returns_full_data(client):
    client.post("/api/qualifications", json=SAMPLE)
    resp = client.get(f"/api/qualifications/{SAMPLE['certificate_number']}")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["holder_name"] == SAMPLE["holder_name"]
    assert data["institution"] == SAMPLE["institution"]


def test_retrieve_unknown_record_returns_404(client):
    resp = client.get("/api/qualifications/DOES-NOT-EXIST")
    assert resp.status_code == 404


def test_retrieve_action_is_logged(client):
    client.post("/api/qualifications", json=SAMPLE)
    client.get(f"/api/qualifications/{SAMPLE['certificate_number']}")
    resp = client.get("/api/audit-log")
    actions = [entry["action"] for entry in resp.get_json()]
    assert "RETRIEVE" in actions


def test_audit_log_filter_by_certificate_number(client):
    other = dict(SAMPLE, certificate_number="MSU-2021-999999", holder_name="Other Person")
    client.post("/api/qualifications", json=SAMPLE)
    client.post("/api/qualifications", json=other)
    resp = client.get("/api/audit-log")
    log = resp.get_json()
    matching = [
        entry for entry in log if entry["certificate_number"] == SAMPLE["certificate_number"]
    ]
    assert len(matching) >= 1


def test_invalid_payload_returns_400(client):
    bad_payload = dict(SAMPLE)
    bad_payload["certificate_number"] = "not-valid"
    resp = client.post("/api/qualifications", json=bad_payload)
    assert resp.status_code == 400

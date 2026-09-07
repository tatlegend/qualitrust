"""
Unit tests: exercise app.verification in isolation.
This is the 'Unit tests' evidence required by the assignment's QA section.
"""
import pytest
from app.verification import (
    validate_certificate_number,
    validate_issue_date,
    validate_registration_payload,
    compute_verification_result,
    ValidationError,
)


class TestCertificateNumberValidation:
    def test_valid_certificate_number(self):
        assert validate_certificate_number("UZ-2023-000451") is True

    def test_missing_certificate_number(self):
        with pytest.raises(ValidationError):
            validate_certificate_number("")

    def test_malformed_certificate_number(self):
        with pytest.raises(ValidationError):
            validate_certificate_number("12345")


class TestIssueDateValidation:
    def test_valid_past_date(self):
        assert validate_issue_date("2023-05-01") is True

    def test_future_date_rejected(self):
        with pytest.raises(ValidationError):
            validate_issue_date("2099-01-01")

    def test_bad_format_rejected(self):
        with pytest.raises(ValidationError):
            validate_issue_date("01/05/2023")


class TestRegistrationPayload:
    VALID_PAYLOAD = {
        "holder_name": "Tendai Moyo",
        "qualification_title": "BSc Information Systems",
        "institution": "University of Zimbabwe",
        "issue_date": "2022-11-15",
        "certificate_number": "UZ-2022-000123",
    }

    def test_valid_payload_passes(self):
        assert validate_registration_payload(self.VALID_PAYLOAD) is True

    def test_missing_field_rejected(self):
        payload = dict(self.VALID_PAYLOAD)
        del payload["institution"]
        with pytest.raises(ValidationError):
            validate_registration_payload(payload)

    def test_short_holder_name_rejected(self):
        payload = dict(self.VALID_PAYLOAD)
        payload["holder_name"] = "T"
        with pytest.raises(ValidationError):
            validate_registration_payload(payload)


class TestVerificationResult:
    def test_not_found_when_record_none(self):
        result = compute_verification_result(None)
        assert result["result"] == "NOT_FOUND"

    def test_verified_when_registered(self):
        record = {
            "status": "REGISTERED",
            "qualification_title": "BSc IS",
            "holder_name": "Tendai Moyo",
            "institution": "UZ",
            "issue_date": "2022-11-15",
        }
        result = compute_verification_result(record)
        assert result["result"] == "VERIFIED"

    def test_revoked_status_detected(self):
        record = {"status": "REVOKED", "institution": "UZ"}
        result = compute_verification_result(record)
        assert result["result"] == "REVOKED"

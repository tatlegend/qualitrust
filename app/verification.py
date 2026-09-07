"""
Core verification engine and validation rules for QualiTrust.
Kept separate from Flask routes so it can be unit-tested in isolation
(no HTTP layer needed) — this is what the CI pipeline's unit-test stage targets.
"""
import re
from datetime import datetime


class ValidationError(Exception):
    """Raised when a qualification record fails validation rules."""
    pass


CERT_NUMBER_PATTERN = re.compile(r"^[A-Z]{2,4}-\d{4}-\d{4,8}$")


def validate_certificate_number(cert_number: str) -> bool:
    """
    Certificate numbers must follow the pattern PREFIX-YEAR-SEQUENCE,
    e.g. UZ-2023-000451, ZIMCHE-2024-1029.
    """
    if not cert_number:
        raise ValidationError("Certificate number is required.")
    if not CERT_NUMBER_PATTERN.match(cert_number):
        raise ValidationError(
            "Certificate number must match PREFIX-YEAR-SEQUENCE, e.g. UZ-2023-000451."
        )
    return True


def validate_issue_date(issue_date: str) -> bool:
    """Issue date must be a valid ISO date and not in the future."""
    try:
        parsed = datetime.strptime(issue_date, "%Y-%m-%d")
    except ValueError:
        raise ValidationError("Issue date must be in YYYY-MM-DD format.")
    if parsed > datetime.utcnow():
        raise ValidationError("Issue date cannot be in the future.")
    return True


def validate_registration_payload(payload: dict) -> bool:
    """Runs all field-level validation rules against a registration payload."""
    required_fields = [
        "holder_name", "qualification_title", "institution",
        "issue_date", "certificate_number",
    ]
    for field in required_fields:
        if not payload.get(field):
            raise ValidationError(f"Field '{field}' is required.")

    if len(payload["holder_name"].strip()) < 2:
        raise ValidationError("Holder name is too short.")

    validate_certificate_number(payload["certificate_number"])
    validate_issue_date(payload["issue_date"])
    return True


def compute_verification_result(record) -> dict:
    """
    Applies business rules to decide whether a stored record counts as
    VERIFIED, REVOKED, or UNVERIFIED, and returns a structured result.
    """
    if record is None:
        return {"result": "NOT_FOUND", "message": "No matching qualification record exists."}

    if record["status"] == "REVOKED":
        return {
            "result": "REVOKED",
            "message": f"This qualification was revoked by {record['institution']}.",
        }

    if record["status"] == "REGISTERED":
        return {
            "result": "VERIFIED",
            "message": (
                f"{record['qualification_title']} awarded to {record['holder_name']} "
                f"by {record['institution']} on {record['issue_date']} is authentic."
            ),
        }

    return {"result": "UNVERIFIED", "message": "Record status could not be determined."}

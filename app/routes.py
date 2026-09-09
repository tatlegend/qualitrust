"""
HTTP layer for QualiTrust. Thin wrappers around app.verification and app.db
so the routes stay easy to read and the logic underneath stays unit-testable.
"""
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template
from app.db import get_db, log_action
from app.verification import (
    validate_registration_payload,
    compute_verification_result,
    ValidationError,
)

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/api/qualifications", methods=["POST"])
def register_qualification():
    payload = request.get_json(force=True)
    try:
        validate_registration_payload(payload)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    db = get_db()
    try:
        db.execute(
            "INSERT INTO qualification "
            "(holder_name, qualification_title, institution, issue_date, "
            "certificate_number, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                payload["holder_name"],
                payload["qualification_title"],
                payload["institution"],
                payload["issue_date"],
                payload["certificate_number"],
                "REGISTERED",
                datetime.utcnow().isoformat(),
            ),
        )
        db.commit()
    except Exception as e:
        return jsonify({"error": f"Could not register qualification: {e}"}), 409

    log_action("REGISTER", payload["certificate_number"], request.remote_addr or "system")
    return jsonify({"message": "Qualification registered successfully."}), 201


@bp.route("/api/qualifications", methods=["GET"])
def search_qualifications():
    query = request.args.get("q", "")
    db = get_db()
    rows = db.execute(
        "SELECT * FROM qualification WHERE holder_name LIKE ? "
        "OR certificate_number LIKE ? OR institution LIKE ?",
        (f"%{query}%", f"%{query}%", f"%{query}%"),
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@bp.route("/api/qualifications/<certificate_number>", methods=["GET"])
def retrieve_qualification(certificate_number):
    """
    Retrieve a single qualification record by its exact certificate number.
    Distinct from /api/verify: this returns the full record (for an
    authorised back-office user), whereas /verify returns only the
    authenticity result (safe to expose to an external checker).
    """
    db = get_db()
    record = db.execute(
        "SELECT * FROM qualification WHERE certificate_number = ?",
        (certificate_number,),
    ).fetchone()

    if record is None:
        return jsonify({"error": "No qualification found with that certificate number."}), 404

    log_action("RETRIEVE", certificate_number, request.remote_addr or "system")
    return jsonify(dict(record))


@bp.route("/api/verify/<certificate_number>", methods=["GET"])
def verify_qualification(certificate_number):
    db = get_db()
    record = db.execute(
        "SELECT * FROM qualification WHERE certificate_number = ?",
        (certificate_number,),
    ).fetchone()

    result = compute_verification_result(record)
    log_action("VERIFY", certificate_number, request.remote_addr or "system", result["result"])
    return jsonify(result)


@bp.route("/api/qualifications/<certificate_number>/revoke", methods=["POST"])
def revoke_qualification(certificate_number):
    db = get_db()
    cur = db.execute(
        "UPDATE qualification SET status = 'REVOKED' WHERE certificate_number = ?",
        (certificate_number,),
    )
    db.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "Certificate not found."}), 404

    log_action("REVOKE", certificate_number, request.remote_addr or "system")
    return jsonify({"message": "Qualification revoked."})


@bp.route("/api/audit-log", methods=["GET"])
def audit_log():
    cert_filter = request.args.get("certificate_number")
    db = get_db()
    if cert_filter:
        rows = db.execute(
            "SELECT * FROM audit_log WHERE certificate_number = ? ORDER BY timestamp DESC",
            (cert_filter,),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM audit_log ORDER BY timestamp DESC").fetchall()
    return jsonify([dict(r) for r in rows])

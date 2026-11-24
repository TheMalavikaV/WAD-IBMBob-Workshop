import traceback

from flask import Flask, jsonify, request

import config
import db
from services import claims as claims_svc
from services import payout as payout_svc
from services import policy as policy_svc
from services import reports
from services.errors import ConflictError, NotFoundError, ValidationError

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
db.init_db()


@app.errorhandler(Exception)
def handle_error(e):
    if isinstance(e, NotFoundError):
        return jsonify({"error": str(e)}), 404
    if isinstance(e, (ValidationError, ConflictError)):
        return jsonify({"error": str(e)}), 400
    return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/policies")
def list_policies():
    status = request.args.get("status")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    return jsonify(policy_svc.list_policies(status, page, page_size))


@app.get("/policies/<policy_id>")
def get_policy(policy_id):
    policy = policy_svc.get_policy(policy_id)
    if policy is None:
        raise NotFoundError(f"Policy {policy_id} not found")
    return jsonify(policy)


@app.post("/quotes")
def quote():
    body = request.get_json()
    premium = policy_svc.calculate_premium(
        body["policy_type"], body["dob"], body["coverage_limit"], body["deductible"]
    )
    return jsonify({"premium": premium})


@app.get("/claims")
def list_claims():
    q = request.args.get("q")
    if q:
        return jsonify(claims_svc.search_claims(q))
    return jsonify(claims_svc.list_claims(request.args.get("status")))


@app.post("/claims")
def file_claim():
    return jsonify(claims_svc.file_claim(request.get_json())), 201


@app.get("/claims/<int:claim_id>")
def get_claim(claim_id):
    claim = claims_svc.get_claim(claim_id)
    if claim is None:
        raise NotFoundError(f"Claim {claim_id} not found")
    return jsonify(claim)


@app.post("/claims/<int:claim_id>/review")
def review(claim_id):
    return jsonify(claims_svc.start_review(claim_id))


@app.post("/claims/<int:claim_id>/approve")
def approve(claim_id):
    body = request.get_json(silent=True) or {}
    return jsonify(claims_svc.approve_claim(claim_id, body.get("approved_amount")))


@app.post("/claims/<int:claim_id>/reject")
def reject(claim_id):
    body = request.get_json(silent=True) or {}
    return jsonify(claims_svc.reject_claim(claim_id, body.get("reason", "")))


@app.post("/claims/<int:claim_id>/pay")
def pay(claim_id):
    return jsonify(payout_svc.pay_claim(claim_id))


@app.get("/reports/summary")
def summary():
    return jsonify(reports.summary())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=config.DEBUG)

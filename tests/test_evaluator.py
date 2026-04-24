from toonflow.evaluator import evaluate_payload


def valid_payload():
    return {
        "id": "eval-001",
        "entity": "invoice",
        "timestamp": "2026-04-23T12:00:00Z",
        "data": {"customer": {"name": "Alice"}, "amount": 245.50},
    }


def test_evaluate_payload_returns_demo_ready_response():
    result = evaluate_payload(valid_payload(), payload_name="invoice")
    assert result["status"] == "ready"
    assert result["validation"]["ok"] is True
    assert result["toon_payload"]
    assert result["extracted_fields"]["data.customer.name"] == "Alice"
    assert result["metrics"]["payload_name"] == "invoice"


def test_evaluate_payload_rejects_invalid_json_contract():
    result = evaluate_payload({"entity": "invoice"})
    assert result["status"] == "rejected"
    assert result["metrics"] is None
    assert result["validation"]["errors"]

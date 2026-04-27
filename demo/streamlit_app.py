from __future__ import annotations

import json
from typing import Any

import streamlit as st

from toonflow.evaluator import evaluate_payload
from toonflow.models import IngestRequest
from toonflow.query import SUPPORTED_OPERATORS, hybrid_query_response
from toonflow.repository import InMemoryRecordStore
from toonflow.service import build_ingest_record, export_record, summarize_record


DEFAULT_PAYLOAD = {
    "id": "demo-006",
    "entity": "cold_chain_shipment",
    "timestamp": "2026-04-25T05:45:00Z",
    "data": {
        "shipment": {
            "shipment_id": "MY-SIN-CC-7781",
            "origin": "Johor Bahru",
            "destination": "Singapore",
            "carrier": "MedLog Asia",
        },
        "limits": {
            "min_temp_c": 2.0,
            "max_temp_c": 8.0,
            "max_shock_g": 3.0,
        },
        "sensor_readings": [
            {
                "at": "2026-04-25T01:00:00Z",
                "facility": "JB-cold-room",
                "temp_c": 4.1,
                "humidity_pct": 61,
                "shock_g": 0.1,
                "battery_pct": 96,
                "within_range": True,
            },
            {
                "at": "2026-04-25T01:30:00Z",
                "facility": "JB-loading",
                "temp_c": 4.8,
                "humidity_pct": 60,
                "shock_g": 0.4,
                "battery_pct": 95,
                "within_range": True,
            },
            {
                "at": "2026-04-25T02:00:00Z",
                "facility": "truck-12",
                "temp_c": 5.2,
                "humidity_pct": 58,
                "shock_g": 0.2,
                "battery_pct": 94,
                "within_range": True,
            },
            {
                "at": "2026-04-25T02:30:00Z",
                "facility": "tuas-checkpoint",
                "temp_c": 6.1,
                "humidity_pct": 57,
                "shock_g": 0.8,
                "battery_pct": 93,
                "within_range": True,
            },
            {
                "at": "2026-04-25T03:00:00Z",
                "facility": "sg-hub",
                "temp_c": 7.4,
                "humidity_pct": 56,
                "shock_g": 1.1,
                "battery_pct": 92,
                "within_range": True,
            },
            {
                "at": "2026-04-25T03:30:00Z",
                "facility": "sg-hub",
                "temp_c": 7.9,
                "humidity_pct": 56,
                "shock_g": 0.3,
                "battery_pct": 91,
                "within_range": True,
            },
            {
                "at": "2026-04-25T04:00:00Z",
                "facility": "clinic-dock",
                "temp_c": 8.4,
                "humidity_pct": 55,
                "shock_g": 0.2,
                "battery_pct": 90,
                "within_range": False,
            },
            {
                "at": "2026-04-25T04:30:00Z",
                "facility": "clinic-fridge",
                "temp_c": 5.0,
                "humidity_pct": 59,
                "shock_g": 0.1,
                "battery_pct": 89,
                "within_range": True,
            },
        ],
        "handoffs": [
            {
                "at": "2026-04-25T00:55:00Z",
                "from_party": "warehouse",
                "to_party": "driver-lee",
                "seal_intact": True,
                "notes": "loaded",
            },
            {
                "at": "2026-04-25T02:22:00Z",
                "from_party": "driver-lee",
                "to_party": "checkpoint",
                "seal_intact": True,
                "notes": "inspected",
            },
            {
                "at": "2026-04-25T03:15:00Z",
                "from_party": "checkpoint",
                "to_party": "sg-hub",
                "seal_intact": True,
                "notes": "cleared",
            },
            {
                "at": "2026-04-25T04:40:00Z",
                "from_party": "sg-hub",
                "to_party": "clinic",
                "seal_intact": True,
                "notes": "delivered",
            },
        ],
    },
}
PAYLOAD_TEXT_KEY = "payload_text_cold_chain_v1"


def _store() -> InMemoryRecordStore:
    if "record_store" not in st.session_state:
        st.session_state.record_store = InMemoryRecordStore()
    return st.session_state.record_store


def _parse_payload(payload_text: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError as exc:
        return None, f"Invalid JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}"
    if not isinstance(payload, dict):
        return None, "Payload must be a JSON object."
    return payload, None


st.set_page_config(page_title="TOONFlow Demo", page_icon="🧾", layout="wide")
st.title("TOONFlow for MariaDB")
st.caption("Validate JSON, convert it to TOON, store queryable fields, and compare JSON vs TOON efficiency.")

with st.sidebar:
    st.header("Demo flow")
    st.markdown(
        """
        1. Paste or edit a JSON payload.
        2. Evaluate validation, TOON output, and metrics.
        3. Ingest the payload into the in-memory demo store.
        4. Query extracted fields and export TOON for AI context.
        """
    )
    if st.button("Reset demo payload"):
        st.session_state[PAYLOAD_TEXT_KEY] = json.dumps(DEFAULT_PAYLOAD, indent=2)
    if st.button("Clear demo store"):
        _store().clear()
        st.success("Demo store cleared.")

if PAYLOAD_TEXT_KEY not in st.session_state:
    st.session_state[PAYLOAD_TEXT_KEY] = json.dumps(DEFAULT_PAYLOAD, indent=2)

payload_text = st.text_area(
    "JSON payload",
    key=PAYLOAD_TEXT_KEY,
    height=360,
)

left, right = st.columns([1, 1])
payload, parse_error = _parse_payload(payload_text)

with left:
    st.subheader("Evaluate")
    if st.button("Validate + convert + benchmark", type="primary"):
        if parse_error or payload is None:
            st.error(parse_error)
        else:
            result = evaluate_payload(payload, str(payload.get("id", "payload")))
            if result["status"] == "rejected":
                st.error("Payload rejected")
                st.json(result["validation"])
            else:
                st.success("Payload is ready")
                metrics = result["metrics"] or {}
                c1, c2, c3 = st.columns(3)
                c1.metric("JSON bytes", metrics.get("json_bytes", 0))
                c2.metric("TOON bytes", metrics.get("toon_bytes", 0))
                c3.metric("Byte savings", f"{metrics.get('byte_savings_percent', 0):.2f}%")
                st.markdown("**TOON payload**")
                st.code(result["toon_payload"], language="text")
                with st.expander("Extracted SQL-friendly fields"):
                    st.json(result["extracted_fields"])

with right:
    st.subheader("Ingest")
    if st.button("Store payload in demo repository"):
        if parse_error or payload is None:
            st.error(parse_error)
        else:
            record = build_ingest_record(IngestRequest(source="streamlit-demo", payload=payload))
            _store().save(record)
            if record.status == "rejected":
                st.error("Payload stored as rejected for audit")
            else:
                st.success(f"Stored payload `{record.payload_id}`")
            st.json(summarize_record(record))

records = _store().list()
st.divider()
st.subheader("Hybrid query + TOON export")

q1, q2, q3 = st.columns([2, 1, 2])
field = q1.text_input("Extracted field", value="entity")
operator = q2.selectbox("Operator", sorted(SUPPORTED_OPERATORS), index=sorted(SUPPORTED_OPERATORS).index("eq"))
value = q3.text_input("Value", value="cold_chain_shipment")

if st.button("Run hybrid query"):
    try:
        response = hybrid_query_response(records, field, value, operator)
    except ValueError as exc:
        st.error(str(exc))
    else:
        st.caption("SQL preview")
        st.code(response["sql_preview"]["sql"], language="sql")
        st.metric("Matched records", response["matched_count"])
        st.json(response["records"])

if records:
    st.subheader("Stored records")
    selected_id = st.selectbox("Select record to export", [record.payload_id for record in records])
    selected_record = next(record for record in records if record.payload_id == selected_id)
    export = export_record(selected_record)
    st.code(export["toon"], language="text")
    with st.expander("Full export payload"):
        st.json(export)
else:
    st.info("No records stored yet. Ingest a payload to try query and export.")

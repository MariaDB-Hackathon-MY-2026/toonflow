from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

from toonflow.evaluator import evaluate_payload
from toonflow.models import IngestRequest
from toonflow.query import SUPPORTED_OPERATORS, hybrid_query_response
from toonflow.repository import InMemoryRecordStore
from toonflow.service import build_ingest_record, export_record, summarize_record


SAMPLE_DIR = Path(__file__).resolve().parents[1] / "data" / "samples"
DEFAULT_SAMPLE = "demo_cold_chain_shipment"
SAMPLE_LABELS = {
    "demo_cold_chain_shipment": "Cold-chain shipment — near corpus average",
    "demo_energy_meter_interval_batch": "Energy meter batch — near corpus average",
    "demo_retail_store_shift": "Retail store shift — high-gain batch",
    "demo_invoice": "Invoice — low-gain control",
    "demo_support_ticket": "Support ticket — text-heavy control",
}


def _load_sample_payloads() -> dict[str, dict[str, Any]]:
    samples: dict[str, dict[str, Any]] = {}
    for path in sorted(SAMPLE_DIR.glob("demo_*.json")):
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, dict):
            samples[path.stem] = payload
    return samples


def _sample_label(sample_name: str) -> str:
    return SAMPLE_LABELS.get(sample_name, sample_name.replace("demo_", "").replace("_", " ").title())


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

sample_payloads = _load_sample_payloads()
sample_names = list(sample_payloads)
default_sample = DEFAULT_SAMPLE if DEFAULT_SAMPLE in sample_payloads else sample_names[0]

if "demo_sample_name" not in st.session_state:
    st.session_state.demo_sample_name = default_sample
if "payload_text" not in st.session_state:
    st.session_state.payload_text = json.dumps(sample_payloads[st.session_state.demo_sample_name], indent=2)

with st.sidebar:
    st.header("Demo flow")
    st.markdown(
        """
        1. Pick a benchmark sample or paste your own JSON payload.
        2. Evaluate validation, TOON output, and per-payload metrics.
        3. Ingest the payload into the in-memory demo store.
        4. Query extracted fields and export TOON for AI context.
        """
    )
    selected_sample = st.selectbox(
        "Benchmark sample",
        sample_names,
        index=sample_names.index(st.session_state.demo_sample_name),
        format_func=_sample_label,
    )
    if selected_sample != st.session_state.demo_sample_name:
        st.session_state.demo_sample_name = selected_sample
        st.session_state.payload_text = json.dumps(sample_payloads[selected_sample], indent=2)

    st.info(
        "The 41.66% byte / 41.67% estimated token savings claim is the weighted total "
        "across the full benchmark corpus. This demo panel reports the selected payload only, "
        "so low-gain controls like the invoice sample are intentionally lower."
    )

    if st.button("Clear demo store"):
        _store().clear()
        st.success("Demo store cleared.")

payload_text = st.text_area(
    "JSON payload",
    key="payload_text",
    height=360,
)

left, right = st.columns([1, 1])
payload, parse_error = _parse_payload(payload_text)
query_value = "invoice" if parse_error or payload is None else str(payload.get("entity", "invoice"))

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
                st.caption("Per-payload result; full-corpus benchmark total is 41.66% byte savings.")
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
value = q3.text_input("Value", value=query_value)

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

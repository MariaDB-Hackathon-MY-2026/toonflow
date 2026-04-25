# JSON vs TOON Benchmark Results

| Payload | JSON bytes | TOON bytes | Byte savings | Token savings | Conversion ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| demo_audit_event_batch | 1584 | 986 | 37.75% | 37.88% | 0.2735 |
| demo_cold_chain_shipment | 1853 | 1086 | 41.39% | 41.25% | 0.2005 |
| demo_energy_meter_interval_batch | 2294 | 1328 | 42.11% | 42.16% | 0.1986 |
| demo_inventory_replenishment | 2120 | 1119 | 47.22% | 47.17% | 0.193 |
| demo_invoice | 184 | 168 | 8.7% | 8.7% | 0.0264 |
| demo_order_fulfillment | 1450 | 972 | 32.97% | 32.87% | 0.1421 |
| demo_patient_observation | 1300 | 826 | 36.46% | 36.62% | 0.1196 |
| demo_retail_store_shift | 3364 | 1693 | 49.67% | 49.7% | 0.2699 |
| demo_service_health_window | 1981 | 1121 | 43.41% | 43.43% | 0.1761 |
| demo_support_ticket | 2309 | 1724 | 25.34% | 25.3% | 0.1833 |
| demo_telecom_cell_kpi_window | 3087 | 1535 | 50.28% | 50.26% | 0.2454 |

## Totals

- JSON bytes: 21526
- TOON bytes: 12558
- Byte savings: 41.66%
- Estimated token savings: 41.67%
- Estimated cost savings: $0.0003363
- Conversion throughput: 5422.99 records/sec

## Baseline comparison

- Reference baseline: pre-polish two-payload sample corpus (2 payloads)
- Baseline savings: 9.39% bytes; 9.56% estimated tokens
- Current savings: 41.66% bytes; 41.67% estimated tokens
- Lift vs baseline: +32.27 percentage points bytes; +32.11 percentage points estimated tokens
- Corpus size: 21526 JSON bytes, 39.64x the baseline JSON byte volume
- The comparison uses the original measured two-payload benchmark as a reference point; it is not a claim that every payload shape will see the same lift.

## Corpus profile

- Profiled payloads: 11 of 11
- Domains covered: billing, cold-chain logistics, commerce/logistics, customer support, energy IoT, healthcare telemetry, retail operations, security/audit, service reliability, telecom operations, warehouse inventory
- Role counts: operational batch: 9, small-document control: 1, text-heavy control: 1

| Payload | Domain | Role | Shape | Why included |
| --- | --- | --- | --- | --- |
| demo_audit_event_batch | security/audit | operational batch | repeated audit event rows with nested batch metadata | models audit exports where repeated scalar event objects are natural |
| demo_cold_chain_shipment | cold-chain logistics | operational batch | sensor readings and handoff rows | models shipment telemetry where tabular readings are expected |
| demo_energy_meter_interval_batch | energy IoT | operational batch | meter interval readings, exception rows, and summary data | models interval meter exports with repeated reading rows |
| demo_inventory_replenishment | warehouse inventory | operational batch | SKU positions, dock schedule rows, and forecast metadata | models inventory planning payloads with repeated SKU rows |
| demo_invoice | billing | small-document control | single compact invoice | keeps a low-gain, non-tabular baseline in the corpus |
| demo_order_fulfillment | commerce/logistics | operational batch | order lines and fulfillment event rows | models order handoff data with repeated line-item structures |
| demo_patient_observation | healthcare telemetry | operational batch | vital readings and medication event rows | models repeated clinical observations plus patient context |
| demo_retail_store_shift | retail operations | operational batch | transactions, inventory movement, cash reconciliation, and alerts | models POS shift close data with repeated reconciliation rows |
| demo_service_health_window | service reliability | operational batch | route metrics, SLO metadata, and deploy events | models production health windows with repeated route metrics |
| demo_support_ticket | customer support | text-heavy control | ticket escalation with messages and reconciliation rows | shows savings are lower when conversational text dominates repeated keys |
| demo_telecom_cell_kpi_window | telecom operations | operational batch | cell KPI rows, alarm events, and operational actions | models RAN monitoring windows with repeated metric rows |

## Role breakdown

| Role | Payloads | JSON bytes | TOON bytes | Byte savings | Token savings |
| --- | ---: | ---: | ---: | ---: | ---: |
| operational batch | 9 | 19033 | 10666 | 43.96% | 43.97% |
| small-document control | 1 | 184 | 168 | 8.7% | 8.7% |
| text-heavy control | 1 | 2309 | 1724 | 25.34% | 25.3% |

## Distribution checks

- Payload count: 11
- Per-payload byte savings range: 8.7% to 50.28%
- Median per-payload byte savings: 41.39%
- Unweighted average per-payload byte savings: 37.75%
- Median per-payload token savings: 41.25%
- Lowest-gain sample: demo_invoice (8.7%)
- Highest-gain sample: demo_telecom_cell_kpi_window (50.28%)
- Weighted totals use full corpus bytes and token estimates, not unweighted per-payload averages.

## Interpretation

Savings are strongest for realistic operational batches with repeated object rows, where TOON's tabular form avoids repeating JSON keys for every row.
The small invoice and text-heavy support ticket remain in the corpus as lower-gain controls, so the totals are not based only on favorable telemetry-style payloads.
Conversion timings are local runtime observations and can vary between runs; byte and token totals are stable for a fixed corpus.

Token and cost values are estimates for repeatable local comparison.

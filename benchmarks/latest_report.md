# JSON vs TOON Benchmark Results

| Payload | JSON bytes | TOON bytes | Byte savings | Token savings | Conversion ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| demo_audit_event_batch | 1584 | 986 | 37.75% | 37.88% | 0.3224 |
| demo_cold_chain_shipment | 1853 | 1086 | 41.39% | 41.25% | 0.1948 |
| demo_energy_meter_interval_batch | 2294 | 1328 | 42.11% | 42.16% | 0.224 |
| demo_inventory_replenishment | 2120 | 1119 | 47.22% | 47.17% | 0.1816 |
| demo_invoice | 184 | 168 | 8.7% | 8.7% | 0.026 |
| demo_order_fulfillment | 1450 | 972 | 32.97% | 32.87% | 0.143 |
| demo_patient_observation | 1300 | 826 | 36.46% | 36.62% | 0.1194 |
| demo_retail_store_shift | 3364 | 1693 | 49.67% | 49.7% | 0.2905 |
| demo_service_health_window | 1981 | 1121 | 43.41% | 43.43% | 0.166 |
| demo_support_ticket | 2309 | 1724 | 25.34% | 25.3% | 0.1839 |
| demo_telecom_cell_kpi_window | 3087 | 1535 | 50.28% | 50.26% | 0.2545 |

## Totals

- JSON bytes: 21526
- TOON bytes: 12558
- Byte savings: 41.66%
- Estimated token savings: 41.67%
- Estimated cost savings: $0.0003363
- Conversion throughput: 5222.92 records/sec

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

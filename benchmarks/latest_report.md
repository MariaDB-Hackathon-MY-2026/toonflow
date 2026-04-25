# JSON vs TOON Benchmark Results

| Payload | JSON bytes | TOON bytes | Byte savings | Token savings | Conversion ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| demo_audit_event_batch | 1584 | 986 | 37.75% | 37.88% | 0.2216 |
| demo_cold_chain_shipment | 1853 | 1086 | 41.39% | 41.25% | 0.1816 |
| demo_invoice | 184 | 168 | 8.7% | 8.7% | 0.0384 |
| demo_order_fulfillment | 1450 | 972 | 32.97% | 32.87% | 0.1425 |
| demo_patient_observation | 1300 | 826 | 36.46% | 36.62% | 0.1193 |
| demo_support_ticket | 359 | 324 | 9.75% | 10.0% | 0.0414 |

## Totals

- JSON bytes: 6730
- TOON bytes: 4362
- Byte savings: 35.19%
- Estimated token savings: 35.2%
- Estimated cost savings: $8.88e-05
- Conversion throughput: 8055.85 records/sec

Token and cost values are estimates for repeatable local comparison.

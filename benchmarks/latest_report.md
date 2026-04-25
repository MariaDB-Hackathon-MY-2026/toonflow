# JSON vs TOON Benchmark Results

| Payload | JSON bytes | TOON bytes | Byte savings | Token savings | Conversion ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| demo_audit_event_batch | 1584 | 986 | 37.75% | 37.88% | 0.2192 |
| demo_cold_chain_shipment | 1853 | 1086 | 41.39% | 41.25% | 0.1823 |
| demo_energy_meter_interval_batch | 2294 | 1328 | 42.11% | 42.16% | 0.2127 |
| demo_inventory_replenishment | 2120 | 1119 | 47.22% | 47.17% | 0.1799 |
| demo_invoice | 184 | 168 | 8.7% | 8.7% | 0.0259 |
| demo_order_fulfillment | 1450 | 972 | 32.97% | 32.87% | 0.1408 |
| demo_patient_observation | 1300 | 826 | 36.46% | 36.62% | 0.1192 |
| demo_service_health_window | 1981 | 1121 | 43.41% | 43.43% | 0.1689 |
| demo_support_ticket | 2309 | 1724 | 25.34% | 25.3% | 0.1809 |

## Totals

- JSON bytes: 15075
- TOON bytes: 9330
- Byte savings: 38.11%
- Estimated token savings: 38.11%
- Estimated cost savings: $0.0002154
- Conversion throughput: 6294.59 records/sec

Token and cost values are estimates for repeatable local comparison.

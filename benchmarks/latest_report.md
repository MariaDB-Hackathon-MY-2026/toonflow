# JSON vs TOON Benchmark Results

| Payload | JSON bytes | TOON bytes | Byte savings | Token savings | Conversion ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| demo_audit_event_batch | 1584 | 986 | 37.75% | 37.88% | 0.2226 |
| demo_cold_chain_shipment | 1853 | 1086 | 41.39% | 41.25% | 0.1882 |
| demo_energy_meter_interval_batch | 2294 | 1328 | 42.11% | 42.16% | 0.1994 |
| demo_inventory_replenishment | 2120 | 1119 | 47.22% | 47.17% | 1.4175 |
| demo_invoice | 184 | 168 | 8.7% | 8.7% | 0.0305 |
| demo_order_fulfillment | 1450 | 972 | 32.97% | 32.87% | 0.152 |
| demo_patient_observation | 1300 | 826 | 36.46% | 36.62% | 0.1254 |
| demo_retail_store_shift | 3364 | 1693 | 49.67% | 49.7% | 0.2822 |
| demo_service_health_window | 1981 | 1121 | 43.41% | 43.43% | 0.2037 |
| demo_support_ticket | 2309 | 1724 | 25.34% | 25.3% | 0.1828 |

## Totals

- JSON bytes: 18439
- TOON bytes: 11023
- Byte savings: 40.22%
- Estimated token savings: 40.23%
- Estimated cost savings: $0.0002781
- Conversion throughput: 3328.56 records/sec

Token and cost values are estimates for repeatable local comparison.

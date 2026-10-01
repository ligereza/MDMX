# BENCH_MATRIX_V1_FINAL

Esta matriz separa lo ya demostrado en software de lo que requiere hardware real.

| Área | Caso | Resultado esperado | Estado |
|---|---|---|---|
| Wire | tamaño FRAMESET | 2068 bytes exactos | PASS host |
| Wire | header | offsets v0.5 canónicos | PASS conformance |
| Wire | CRC | CRC-32/ISO-HDLC sobre [0,2064) | PASS conformance |
| Parser | golden válido | commit + ACK | PASS conformance |
| Parser | CRC corrupto | ERR_CRC, sin commit | PASS conformance |
| Sequence | duplicate | ACK, Δgen=0 | PASS conformance |
| Sequence | stale | ERR_SEQUENCE, Δgen=0 | PASS conformance |
| Sequence | wrap | comparación modular válida | contrato congelado |
| Host | partial write | completar frame | PASS mock |
| Host | backpressure | no corromper frame | PASS mock |
| Host | timeout/retry | retransmitir idéntico | PASS mock |
| Host | reconnect | recuperar transporte | PASS mock |
| Atomicidad | 4 universos | swap lógico único | PASS lógico / HIL pendiente |
| Failsafe | sin FrameSet válido 500 ms | HOLD último estado | HIL pendiente |
| Startup | antes del primer frame | drivers OFF | HIL pendiente |
| DMX | baud | 250000 | físico pendiente |
| DMX | serial | 8N2 | físico pendiente |
| DMX | BREAK | ≥92 µs; objetivo 176 µs | físico pendiente |
| DMX | MAB | ≥12 µs | físico pendiente |
| DMX | slot | ~44 µs | físico pendiente |
| DMX | cadencia | referencia ~43.94 Hz; objetivo ~40 Hz | físico pendiente |
| OUT4 | simultaneidad | 4 salidas activas | físico pendiente |
| OUT4 | skew | medir entre salidas | pendiente |
| Electrical | aislamiento | comprobar por salida | pendiente |
| Electrical | terminación bench | 120 Ω donde corresponda | pendiente |
| Reliability | burn-in | sin corrupción/pérdida indebida | pendiente |
| Reliability | error budget | cuantificar sostenidamente | pendiente |

## Interpretación

Los PASS de protocolo y host son reales pero **no equivalen** a un PASS físico.

No promover el proyecto a “hardware validado” hasta completar HIL y mediciones eléctricas/temporales.

# Estado canónico — MDMX

Fecha de consolidación: 2026-10-01.

## Congelado

### Arquitectura
`DMX/Art-Net/sACN → Semantic Frame → Expansion Engine → 4×512 → USB CDC → RP2040/MDMX-OUT4 → 4 DMX`.

### MCU / OUT4
- RP2040 como objetivo válido.
- PIO preferido para temporización DMX.
- DMA para alimentar salidas.
- 4 salidas DMX independientes.
- Doble banco: `active[4][512]` + `pending[4][512]`.
- Commit atómico del FrameSet.
- CRC + ACK/NACK + secuenciación.
- HOLD tras 500 ms sin FrameSet válido.
- Drivers OFF antes del primer FrameSet válido.
- Aislamiento por salida.

### Protocolo
- `FRAMESET_V1`.
- Variante canónica: `v0.5-2068`.
- Total: 2068 bytes.
- CRC-32/ISO-HDLC.
- Reply fija de 8 bytes.
- Duplicados se ACKean sin segundo commit.
- Secuencias stale se rechazan.

## Evidencia aprobada

- `PROTOCOL_CONFORMANCE_PASS`: **4/4**.
- Harness USB CDC host-side: **10/10 PASS** en mock.
- Fixtures canónicos de interoperabilidad identificados por SHA-256 y CRC.
- `BENCH_MATRIX_V1_FINAL` cerrada como contrato de aceptación.

## No demostrado todavía

- Fuente canónica completa del firmware v0.2.
- Build reproducible del firmware actual.
- `BUILD_PASS`.
- USB CDC contra RP2040 real.
- PIO/DMA sobre placa real.
- 4 salidas simultáneas medidas.
- Atomicidad observada físicamente.
- HOLD de 500 ms medido en HIL.
- BREAK/MAB y cadencia medidos.
- Aislamiento y comportamiento eléctrico medidos.
- Burn-in / error budget sostenido.

## Estado de recuperación de firmware

`SOURCE_RECOVERY_EXHAUSTED`.

Esto no invalida el protocolo ni las pruebas host. Significa que la implementación física debe ser reconstruida o reintroducida antes de reclamar HIL o PASS físico.

## Próximo gate

```text
SOURCE/IMPLEMENTATION
        ↓
BUILD_PASS
        ↓
USB_CDC_HIL_PASS
        ↓
DMX_TIMING_PASS
        ↓
DMX_ELECTRICAL_PASS
        ↓
OUT4_SIMULTANEOUS_PASS
        ↓
BURN_IN_PASS
```

# Firmware RP2040 — contrato de reconstrucción

## Estado

La arquitectura del firmware está congelada, pero el source canónico v0.2 no fue recuperado.

Estado histórico: **SOURCE_RECOVERY_EXHAUSTED**.

Por lo tanto, este directorio no debe fingir un `BUILD_PASS` inexistente.

## Objetivo

Implementar exactamente:

```text
USB CDC ACM
    ↓
parser FRAMESET_V1
    ↓
CRC / formato / secuencia
    ↓
pending[4][512]
    ↓
commit atómico
    ↓
active[4][512]
    ↓
4 × PIO + DMA
    ↓
DMX OUT1..OUT4
```

## Invariantes

- `active[4][512]` nunca se modifica parcialmente por un FrameSet recibido.
- `pending[4][512]` se llena y valida antes del commit.
- CRC inválido → `ERR_CRC`, sin commit.
- Formato inválido → `ERR_FORMAT`, sin commit.
- Secuencia stale → `ERR_SEQUENCE`, sin commit.
- Duplicado → ACK sin nuevo commit.
- Secuencia nueva válida → commit único.
- ACK de secuencia nueva después del commit.
- Drivers OFF antes del primer FrameSet válido.
- Ausencia de FrameSet válido por 500 ms → HOLD del último estado válido.

## Emisión DMX

Objetivo congelado:

- 250000 baud.
- 8N2.
- BREAK: objetivo histórico 176 µs; aceptación nunca menor a 92 µs.
- MAB: 12 µs mínimo/objetivo registrado.
- Slot: ~44 µs.
- Cadencia de referencia: ~43.94 Hz para universo completo; operación objetivo ~40 Hz.
- PIO preferido a UART.
- DMA para continuidad.

## Siguiente evidencia requerida

1. source implementado/reintroducido;
2. build reproducible;
3. `BUILD_PASS`;
4. CDC real;
5. parser/ACK real;
6. PIO/DMA medido;
7. cuatro salidas concurrentes;
8. failsafe/HOLD físico;
9. burn-in.

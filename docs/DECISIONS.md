# Decisiones, descartes y reglas de no-regresión

## D-001 — Frontera semántica

**Decisión:** Semantic Frame/Expansion Engine vive en Linux/Raspberry/host. MDMX-OUT4 es semánticamente ciego.

No mover IA, perfiles, autoidentificación, X/Y/Z ni efectos al MCU.

## D-002 — Cuatro buffers finales

El host entrega cuatro universos completos de 512 bytes. No enviar una representación semántica comprimida al RP2040.

## D-003 — RP2040 + PIO/DMA

Arquitectura congelada para OUT4. Se descartó seguir abriendo la comparación UART vs PIO como decisión arquitectónica; PIO queda como camino canónico.

## D-004 — Commit atómico

Los cuatro universos forman una unidad lógica. Un error en cualquier parte del FrameSet no puede dejar salidas en generaciones diferentes.

## D-005 — FRAMESET_V1 / v0.5-2068

Único wire contract vigente.

Rechazado:
- 2076 bytes;
- header de 24 bytes;
- wrapper de compatibilidad;
- campos `port_count/slot_count/reserved`;
- variantes históricas incompatibles de v0.4.

## D-006 — Idempotencia de retry

Host stop-and-wait. Retries idénticos. Duplicado válido recibe ACK sin segundo commit.

## D-007 — Failsafe

Después de 500 ms sin FrameSet válido, mantener HOLD del último estado válido. No inventar blackout dentro de este contrato.

Antes del primer FrameSet válido, drivers OFF.

## D-008 — Bring-up OUT1 antes de OUT4

Validar una salida física completa antes de replicar cuatro veces.

## D-009 — Evidencia

Mock ≠ HIL.

Conformance wire ≠ hardware físico.

No declarar `BUILD_PASS`, `USB_CDC_HIL_PASS` ni `DMX_PHYSICAL_PASS` sin evidencia correspondiente.

## D-010 — Fixtures

Los fixtures congelados se identifican por SHA-256. No regenerarlos silenciosamente con una receta “equivalente”.

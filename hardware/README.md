# MDMX-OUT4 — hardware

## Objetivo

Dispositivo USB a cuatro salidas DMX físicamente independientes y aisladas.

## Núcleo

- MCU: RP2040 como objetivo congelado.
- USB: CDC ACM.
- Generación DMX: PIO + DMA.
- Salidas: 4.
- Física: RS-485 compatible con DMX.
- Conector objetivo: XLR-5.
- Aislamiento: por salida.
- Protección de línea/alimentación: obligatoria para el diseño final.

## Topología conceptual de cada salida

```text
RP2040 / PIO
    ↓
aislamiento
    ↓
transceiver RS-485
    ↓
protección
    ↓
XLR-5 DMX OUT
```

La selección exacta de componentes todavía pertenece al BOM/compra y debe ser validada contra tensión, velocidad, aislamiento y disponibilidad real.

## Terminación

La matriz conserva **120 Ω** como valor de terminación DMX de referencia al final de línea.

No se decidió instalar terminadores permanentes dentro de cada salida MDMX-OUT4; el bench debe poder ensayar la línea de forma correcta sin convertir la terminación en una carga fija interna no deseada.

## Estrategia de bring-up

Antes de fabricar/replicar OUT4:

1. construir **OUT1 de laboratorio**;
2. validar MCU → aislamiento → transceiver → protección → XLR-5;
3. medir BREAK/MAB;
4. verificar 250 kbaud / 8N2;
5. verificar cadencia;
6. probar pérdida de host y HOLD;
7. recién entonces replicar ×4.

## No aprobado todavía

- esquema eléctrico final;
- PCB final;
- selección definitiva de transceiver/aislador/protección;
- alimentación final;
- mediciones físicas;
- skew entre salidas;
- burn-in.

Ver [PURCHASES.md](PURCHASES.md) para el BOM operativo en preparación.

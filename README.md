# MDMX

MDMX es la capa física/determinista de salida DMX del proyecto. La capa semántica común es **X-ANALOGIA-X**: MDMX actúa como backend físico de su ontología/DSL y emite DMX real sin reinterpretar esa intención dentro del MCU.

## Arquitectura canónica

```text
DMX / Art-Net / sACN
        ↓
Linux / Raspberry Pi
Semantic Frame
        ↓
Expansion Engine
        ↓
4 × 512 bytes DMX finales
        ↓
USB CDC ACM
FRAMESET_V1
        ↓
RP2040 + PIO/DMA
MDMX-OUT4
        ↓
4 salidas DMX aisladas
```

La frontera es deliberada: **Semantic Frame / Expansion Engine decide comportamiento; MDMX-OUT4 sólo transmite determinísticamente**.

El MCU no contiene IA, perfiles de luminarias, autoidentificación ni lógica X/Y/Z/efectos.

## Estado

- FRAMESET_V1 / v0.5-2068: **FROZEN**
- Conformance independiente: **4/4 PASS**
- Host USB CDC mock: **10/10 PASS**
- RP2040 + PIO/DMA + 4 salidas: arquitectura **FROZEN**
- Firmware canónico v0.2: **SOURCE_RECOVERY_EXHAUSTED**
- BUILD_PASS: pendiente
- USB CDC HIL real: pendiente
- DMX físico/eléctrico/timing: pendiente

El siguiente límite del proyecto es físico: reconstruir/implementar el firmware canónico, compilarlo y validar la cadena completa USB CDC → RP2040 → DMX.

## Índice

- [Estado canónico](STATUS.md)
- [Arquitectura](docs/ARCHITECTURE.md)
- [Integración canónica X-ANALOGIA-X ↔ MDMX ↔ MTRACK](docs/XANALOGIA_INTEGRATION.md)
- [MTRACK: percepción/cámara/3D](docs/MTRACK_ARCHITECTURE.md)
- [FRAMESET_V1](docs/FRAMESET_V1.md)
- [Host USB CDC](host/README.md)
- [Firmware RP2040](firmware/README.md)
- [Hardware MDMX-OUT4](hardware/README.md)
- [Fixtures congelados](fixtures/README.md)
- [BENCH_MATRIX_V1_FINAL](docs/BENCH_MATRIX_V1_FINAL.md)
- [Benchmark semántico](docs/SEMANTIC_BENCHMARK.md)
- [Decisiones y descartes](docs/DECISIONS.md)
- [Traspaso desde “Director”](docs/DIRECTOR_HANDOFF.md)
- [Compras / BOM](hardware/PURCHASES.md)

> Regla de trabajo: no reabrir protocolo, CRC, fixtures ni arquitectura semántica del MCU salvo evidencia nueva que invalide una decisión congelada.

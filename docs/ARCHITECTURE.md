# Arquitectura MDMX

## Principio central

MDMX separa completamente la **semántica** de la **emisión física**.

La capa superior puede entender luminarias, PAN/TILT, X/Y/Z, dimmer, efectos, espejo, spread, remapeos o cualquier transformación. El MCU no necesita conocer nada de eso.

```text
Entradas de show
DMX / Art-Net / sACN
        ↓
Linux / Raspberry Pi
        ↓
Semantic Frame
        ↓
Expansion Engine
        ↓
Universos DMX finales
OUT1 | OUT2 | OUT3 | OUT4
        ↓
FRAMESET_V1 por USB CDC ACM
        ↓
RP2040
        ↓
PIO/DMA
        ↓
4 buses RS-485/DMX aislados
```

## Responsabilidad de Semantic Frame / Expansion Engine

- Interpretar y mantener significado.
- Resolver mappings.
- Resolver relaciones entre parámetros.
- Generar efectos y transformaciones.
- Producir exactamente cuatro buffers DMX finales de 512 bytes.

## Responsabilidad de MDMX-OUT4

- Recibir un FrameSet completo.
- Validar formato, CRC y secuencia.
- Mantener staging separado de active.
- Hacer commit atómico.
- Emitir los cuatro universos de forma determinista.
- Mantener temporización DMX válida.
- Aplicar el failsafe definido.

## Lo que MDMX-OUT4 NO hace

- No contiene IA.
- No descubre fixtures.
- No interpreta perfiles de luminarias.
- No conoce X/Y/Z.
- No genera PAN espejo.
- No genera spread, delay ni efectos.
- No decide qué slots están relacionados.
- No comprime la representación semántica.

## Motivo

El hardware debe ser una frontera estable. Si la inteligencia cambia, se actualiza arriba. El dispositivo físico conserva un contrato pequeño: cuatro framebuffers opacos entran, cuatro universos DMX salen.

Esto permite que MDMX se conecte posteriormente con capas más inteligentes sin reabrir el dispositivo de salida.

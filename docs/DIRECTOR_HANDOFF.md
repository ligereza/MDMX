# Handoff del chat “Director”

Este repositorio fue inicializado después de que el hilo de trabajo “Director” alcanzara su límite. Este archivo conserva el estado de continuidad para que el proyecto no dependa del historial del chat.

## Resultado consolidado

La investigación cerró una arquitectura en dos lados:

### Fuera de MDMX-OUT4
- DMX / Art-Net / sACN.
- Linux/Raspberry Pi.
- Semantic Frame.
- Expansion Engine.
- generación de cuatro universos finales.

### Dentro de MDMX-OUT4
- USB CDC ACM.
- FRAMESET_V1.
- parser/CRC/secuencia.
- staging + commit atómico.
- RP2040.
- PIO/DMA.
- cuatro salidas DMX aisladas.

## Hitos cerrados

- FRAMESET_V1 reconciliado byte a byte.
- v0.5-2068 aceptado.
- 2076/v0.4 histórica rechazadas.
- fixtures congelados.
- `PROTOCOL_CONFORMANCE_PASS` 4/4.
- host USB CDC 10/10 en mock.
- matriz de aceptación final preparada.
- arquitectura RP2040+PIO/DMA congelada.

## Incidente de continuidad

El firmware canónico v0.2 que históricamente se describió como existente no pudo recuperarse como source verificable.

Estado final de recuperación:

```text
SOURCE_RECOVERY_EXHAUSTED
```

Por eso quedaron bloqueados:

```text
BUILD_PASS
USB_CDC_HIL_PASS
DMX_ELECTRICAL_PASS
DMX_TIMING_PASS
```

El proyecto no debe “rellenar” esta ausencia afirmando que el firmware ya está validado. Debe reconstruirlo contra el contrato congelado.

## Próxima etapa acordada

1. trasladar el estado canónico al repo;
2. preparar BOM equivalente en AliExpress, Amazon y Chile/Santiago;
3. montar OUT1 de laboratorio;
4. reconstruir firmware;
5. build;
6. HIL;
7. replicar OUT4;
8. medir y cerrar aceptación física.

## Regla para agentes futuros

Leer primero:
1. `STATUS.md`
2. `docs/ARCHITECTURE.md`
3. `docs/FRAMESET_V1.md`
4. `docs/DECISIONS.md`
5. `docs/BENCH_MATRIX_V1_FINAL.md`

No reinterpretar el historial desde cero si esos documentos no han sido invalidados por nueva evidencia.

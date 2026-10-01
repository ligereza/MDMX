# Benchmark semántico / Expansion Engine

Este documento registra la demostración usada para separar la capa semántica de MDMX-OUT4.

## Fixture conceptual

Fuente semántica registrada:

```text
C0 80 60 FF 40 00 C0 80 80 40
```

10 slots/variables de entrada alimentan una expansión sobre múltiples fixtures.

Posiciones normalizadas registradas:

```text
[-1, -0.714, -0.429, -0.143, 0.143, 0.429, 0.714, 1]
```

La implementación histórica usó cuantización q8/q16 con round-half-up.

## Ejemplo de expansión

- OUT1: normal.
- OUT2: PAN invertido / espejo.
- OUT3: remapeado.
- OUT4: transformación procedural dependiente de la capa superior.
- X/Y/Z pueden compartir dimmer mientras otros atributos permanecen transformados independientemente.

Estas transformaciones ocurren **antes** de FRAMESET_V1. Para el RP2040 son simplemente bytes.

## CER

En la prueba conceptual:

- 10 grados/variables semánticas de entrada;
- 256 slots físicos gobernados en el ejemplo;
- `CER = 256 / 10 = 25.6`.

El CER mide expansión/control derivado, **no** crea 256 grados de libertad independientes.

OUT2/OUT3/OUT4 derivados siguen dependiendo de los 10 grados semánticos de origen.

## Objetivo del benchmark

Medir por separado:

- slots de entrada;
- variables semánticas;
- slots de salida;
- grados de libertad independientes;
- ratio de expansión.

La conclusión arquitectónica fue mantener esta lógica fuera del MCU.

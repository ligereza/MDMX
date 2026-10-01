# FRAMESET_V1 — v0.5-2068

**Estado: FROZEN**

## Tamaño total

```text
16 bytes   header
2048 bytes payload = 4 × 512
4 bytes    CRC
--------------------
2068 bytes total
```

## Header — 16 bytes

| Offset | Tamaño | Campo | Valor / formato |
|---:|---:|---|---|
| 0–3 | 4 | magic | ASCII `MDMX` |
| 4 | 1 | version | `0x01` |
| 5 | 1 | type | `0x01` |
| 6–7 | 2 | header_len | `16`, uint16 LE |
| 8–11 | 4 | sequence | uint32 LE |
| 12–13 | 2 | payload_len | `2048`, uint16 LE |
| 14–15 | 2 | flags | `0`, uint16 LE |

Header exacto para `sequence=1`:

```text
4D444D58010110000100000000080000
```

## Payload

| Rango | Contenido |
|---|---|
| 16–527 | OUT1, 512 bytes |
| 528–1039 | OUT2, 512 bytes |
| 1040–1551 | OUT3, 512 bytes |
| 1552–2063 | OUT4, 512 bytes |

Los buffers son opacos para el MCU.

## CRC

- Algoritmo: **CRC-32/ISO-HDLC**.
- Cobertura: bytes `[0, 2064)`, es decir header + payload.
- Almacenamiento: uint32 little-endian en bytes 2064–2067.

Vector/oráculo histórico recuperado:

- CRC: `0x4C5E722F`
- bytes LE: `2F 72 5E 4C`
- SHA-256 asociado: `ae6c1cc94207c26a3567dde634bce984b7f01478eb06ce535804538789f1cfe9`

## Reply

Reply exacta: **8 bytes**.

```text
'M' 'R' | version=1 | status | sequence:u32le
```

Estados:

| status | significado |
|---:|---|
| `0x00` | ACK |
| `0x01` | ERR_CRC |
| `0x02` | ERR_FORMAT |
| `0x03` | ERR_SEQUENCE |

## Semántica de commit

El ACK de un FrameSet nuevo sólo ocurre después de validación y commit atómico.

Un FrameSet inválido no puede modificar `active`.

## Secuencias

Comparación modular uint32:

- `delta == 0`: duplicado → ACK, sin segundo commit.
- `0 < delta < 0x80000000`: secuencia nueva.
- `delta >= 0x80000000`: stale → `ERR_SEQUENCE`.
- Wrap uint32 válido.

## Transporte

El host usa comportamiento stop-and-wait. Los retries reutilizan el mismo FrameSet y la misma secuencia; el receptor debe hacer el retry idempotente mediante la regla de duplicados.

## Variantes rechazadas

Quedan explícitamente fuera del contrato:

- Formato de **2076 bytes**.
- Header de **24 bytes**.
- Campos históricos `port_count`, `slot_count`, `reserved`.
- Variante `v0.4-2068` incompatible con los offsets canónicos finales.
- Cualquier wrapper adicional alrededor de FRAMESET_V1.

No reabrir estas variantes.

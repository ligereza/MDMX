# Fixtures canónicos FRAMESET_V1

**Estado lógico: FROZEN.**

Los blobs originales no están materializados todavía en este repositorio. Sus identidades conocidas se registran aquí para evitar regenerarlos de forma accidental e incompatible.

## golden-1.bin

- sequence: 1
- timestamp semántico histórico: 0 µs
- CRC almacenado: `854D156B`
- SHA-256: `6d5ebd58e7ee4f9ee7a64fe28d50c4c53db1707ca9ae23d1752e1c8b1619cbb0`

## golden-2.bin

- sequence: 2
- timestamp semántico histórico: 250000 µs
- CRC almacenado: `1E5741CF`
- SHA-256: `134317a20c96d4b2c4f686743a208e45ea235ebede0f0e06592604974a5d558a`

## golden-3.bin

- sequence: 3
- timestamp semántico histórico: 500000 µs
- CRC almacenado: `67EE8D41`
- SHA-256: `ae3a1dee5d1f36a26f3cec99afb215368a646ca347ac2bdf83218cda6a1cbe0c`

## corrupt-out1-seq2.bin

Derivado de `golden-2.bin`:

```text
byte[16] ^= 0x01
```

El CRC almacenado permanece `1E5741CF`, mientras el CRC recalculado pasa a `96E1FBAC`.

Resultado esperado:

- `ERR_CRC`;
- cero commit;
- active sin cambios.

SHA-256:
`90754445b5240317abc8a7cd261bf56c1d604a3f116e5b0c3801d4340a85df68`

## Recuperación

Un blob recuperado sólo se acepta si su SHA-256 coincide exactamente con el valor congelado correspondiente.

No regenerar fixtures y reemplazarlos silenciosamente.

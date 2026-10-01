# Host USB CDC

## Rol

El host corre sobre Linux/Raspberry Pi o PC y recibe los cuatro universos ya expandidos. Serializa FRAMESET_V1, lo envía por USB CDC ACM y procesa la reply del dispositivo.

## Contrato

- Frame fijo de 2068 bytes.
- Stop-and-wait.
- Un FrameSet en vuelo.
- Retry idéntico: mismos 2068 bytes y misma secuencia.
- ACK sólo cierra la transacción correspondiente.
- Reconnect debe recuperar el transporte sin alterar el contrato wire.

## Pruebas host-side

El harness USB CDC alcanzó **10/10 PASS en mock**.

Los escenarios registrados incluyen:

- partial writes;
- backpressure;
- ACK;
- NACK;
- timeout + retry;
- duplicate;
- stale;
- reconnect;
- reglas congeladas de protocolo.

Este PASS demuestra el comportamiento del cliente y del contrato contra un mock. **No prueba firmware, placa ni DMX físico.**

## Artefactos históricos

En “Director” se trabajó con mdmx-bench y fixtures binarios congelados. El source/paquete original no está presente todavía en este repositorio.

Cuando se reintroduzca código host, debe consumir literalmente el contrato de ../docs/FRAMESET_V1.md, no reinterpretarlo.

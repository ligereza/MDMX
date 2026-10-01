# X-ANALOGIA-X ↔ MDMX ↔ MTRACK

Estado: decisión arquitectónica, 2026-10-01.

Este documento fija la conexión entre MDMX y X-ANA-X. La decisión central es que **MDMX no tendrá una ontología ni un lenguaje semántico paralelo**. X-ANALOGIA-X es el motor común; MDMX es uno de sus backends físicos y MTRACK es una fuente de observación/calibración del mismo mundo.

## 1. Un solo motor y un solo lenguaje

```text
                         X-ANALOGIA-X
                MOTOR / ONTOLOGÍA / DSL

 Fixture · Attribute · Selection ordenada
 Group · Palette/Preset · Cue/Sequence
 Programmer · Effect · Time · Reference
 State/History · Geometry · Loss · Evidence

 interp · affine · permutation · quantize
 compose · waveform · selectors · state machine
                           │
          ┌────────────────┼────────────────┐
          │                │                │
     adapter MA       adapter Titan    backend MDMX
          │                │                │
      consola/show      consola/show    SemanticFrame
                                            │
                                      Expansion Engine
                                            │
                                       DMX físico
```

Una operación abstracta no pertenece a MA, Titan ni MDMX. Por ejemplo:

```text
RAMP(selection, a, b)
   ├── bajar(MA)    → programa/sintaxis MA
   ├── bajar(Titan) → programa/sintaxis Titan
   └── bajar(MDMX)  → expansión física sobre fixtures/universos
```

MDMX no necesita aprender cómo Titan llama una operación ni cómo MA la presenta. Consume la representación común ya elevada al espacio abstracto.

## 2. Traducción de shows

La misma representación permite copiar un show entre sistemas:

```text
grandMA3 show
    ↓ elevar
grafo tipado X-ANALOGIA-X
    ↓ bajar
Avolites Titan show
```

El objetivo no es copiar bytes ni comandos, sino preservar significado. La traducción entrega dos veredictos independientes:

- **equivalencia observable:** el resultado producido coincide o queda acotado por un error ε;
- **equivalencia estructural:** se preservan grupos, orden, paletas/presets, cues, referencias vivas, tracking, tiempos, efectos y otras relaciones del grafo.

Cuando el destino no puede representar una relación se genera una pérdida explícita. Ejemplo: una referencia viva puede degradarse a valores absolutos, pero esa degradación nunca se oculta.

## 3. Papel exacto de MDMX

MDMX sigue siendo la capa física/determinista. El RP2040 permanece semánticamente ciego.

```text
X-ANALOGIA-X
      ↓ operación/estado abstracto
backend MDMX
      ↓
Semantic Frame
      ↓
Expansion Engine
      ↓
4 × 512 bytes DMX finales
      ↓
FRAMESET_V1
      ↓
RP2040 + PIO/DMA
      ↓
MDMX-OUT4
```

`FRAMESET_V1`, atomic commit, HOLD y la salida DMX congelada no cambian por esta decisión. La inteligencia vive antes de la frontera determinista.

## 4. MDMX512

MDMX512 se conserva como posible superficie compacta de control, pero **no debe convertirse en un catálogo cerrado de efectos**. Debe transportar operaciones y referencias del lenguaje común: selección/grupo, atributo, operación, parámetros, composición y tiempo.

Un universo de control puede producir varios universos físicos solo cuando el resultado es derivable desde estructura compartida. No significa comprimir arbitrariamente 2048 bytes independientes dentro de 512.

## 5. MTRACK no crea otra semántica

MTRACK observa el mismo mundo que modela X-ANALOGIA-X:

```text
intención abstracta
       ↓
backend / consola
       ↓
mundo físico
       ↓
cámaras / sensores
       ↓
MTRACK
       ↓
observaciones XYZ + confianza + procedencia
       ↓
modelo del mundo X-ANALOGIA-X
```

MTRACK aporta hechos espaciales y residuales, no nombres de operaciones ni decisiones de show. El motor común decide cómo esas observaciones actualizan calibraciones, hipótesis o estado.

## 6. Gemelo 3D calibrable

El 3D no se usa solo como visualizador tipo Capture. Es un **world model / digital twin** que conoce fixture, pose, geometría, superficies, cámaras, FOV, óptica, zonas, haces e intersecciones.

```text
comando abstracto
      ↓
predicción 3D
      ↓
resultado esperado
      ↕ residual
observación real MTRACK
```

El residual entre predicción y observación es señal de calibración/aprendizaje. La cámara nunca es verdad absoluta: tiene pose, FOV, oclusión, latencia, ruido y confianza.

## 7. CCTV existente como ObservationSource

MTRACK debe preferir cámaras existentes del venue cuando exista autorización. La unidad base es `ObservationSource`, no una cámara propietaria de MDMX.

Fuentes posibles:

- CCTV RTSP/ONVIF;
- cámara propia MDMX;
- PTZ;
- simulador 3D;
- metadata externa;
- futuros sensores.

Topología prevista:

```text
red CCTV / VLAN del venue
          │
     1 Ethernet
          │
        MTRACK
    ┌─────┼─────┐
  cam-A cam-B cam-N
```

ONVIF/RTSP es la primera ruta; Hikvision es el primer banco real porque existen dos cámaras disponibles para pruebas.

## 8. Privacidad por diseño

Modo por defecto:

```text
stream → RAM → detección/geometría/XYZ → descartar frame
```

No persistir por defecto video, frames, rostros, embeddings biométricos ni identidad personal. Sí pueden persistir intrínsecos/extrínsecos, pose, cobertura, XYZ, confianza, calibraciones, residuos y métricas. Un `track_id` representa continuidad geométrica efímera, no identidad humana.

## 9. Calibración y aprendizaje

Las calibraciones siguen un ciclo obligatorio:

```text
COLLECT → CANDIDATE → VALIDATED → ACTIVE → STALE
```

Ningún modelo aprendido pasa directamente de datos a `ACTIVE`. Un cambio de cámara, resolución, crop, lente, zoom o pose puede volver una calibración `STALE`.

El aprendizaje físico busca inicialmente:

```text
F(command, fixture, geometry, state) → resultado observado
```

y después la inversa:

```text
F⁻¹(objetivo visual/espacial) → control
```

## 10. Confianza, tiempo y autoridad

La confianza combina detector, calibración, salud de fuente, antigüedad y cobertura válida. Dos cámaras se fusionan solo si comparten coordenadas y tiempo suficientemente alineado; rayos casi paralelos no dan profundidad confiable.

La latencia visible es la suma de exposición, encode, red, decode, inferencia, fusión, estimación temporal, compilación, salida y mecánica del fixture. FPS por sí solo no resuelve tracking.

MTRACK toma autoridad **por atributo**, no por fixture completo. Un lease puede permitir que MTRACK controle PAN/TILT mientras la consola conserva dimmer, color, gobo o zoom.

## 11. Límite del núcleo histórico

`XANAX.Core` histórico no debe crecer como segundo cerebro paralelo. Sus piezas útiles —codecs GDTF/DMX, modelos de comportamiento, Jacobiano u otras matemáticas— se evalúan como ajustadores, adaptadores o utilidades del motor X-ANALOGIA-X. La ontología y la verdad del sistema viven una sola vez.

## 12. Regla para futuras implementaciones

Antes de agregar una semántica nueva a MDMX preguntar: **¿esto pertenece al lenguaje común de X-ANALOGIA-X o es únicamente una realización física del backend MDMX?**

Si describe intención, estructura, estado, referencia, equivalencia o pérdida, pertenece al motor común. Si convierte esa intención validada en bytes/universos/salida física, pertenece a MDMX.

## Documentos relacionados

- `docs/MTRACK_ARCHITECTURE.md`
- `docs/MTRACK_CCTV_INGEST.md`
- `docs/MTRACK_LIMITS.md`
- `docs/MTRACK_DATA_MODEL.md`
- `docs/MTRACK_TWO_HIKVISION_LAB.md`
- `docs/MDMX512_CONTROL_PLANE.md`
- En X-ANA-X: `PUPILA/avolites/docs/xanalogia_lab_diseno.md`
- En X-ANA-X: `XANALOGIA_MDMX_ARCHITECTURE.md`

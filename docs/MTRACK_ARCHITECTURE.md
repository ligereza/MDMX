# MTRACK — camera/3D feedback layer

Status: EXPERIMENTAL. Branch: MTRACK.

MTRACK is the perception and calibration layer for MDMX. It does not replace the deterministic DMX output path.

## Core loop

```
Rig model / 3D scene
        |
        v
Predicted visual state
        |
        +---------------------+
        |                     |
        v                     v
MDMX output              virtual cameras
        |                     |
        v                     |
real fixtures                 |
        |                     |
        v                     |
camera observations ----------+
        |
        v
world-space observations
        |
        v
prediction error / confidence
        |
        +--> calibration correction
        +--> tracking
        +--> learned fixture response
```

The camera is never treated as absolute truth. It is one sensor with a calibrated pose, field of view, uncertainty, occlusion and potentially bad depth.

## Useful ideas adopted clean-room

### From SlyLED

Architectural ideas only; no source code copied.

- independent camera nodes;
- camera intrinsic calibration;
- extrinsic camera pose in stage coordinates;
- ArUco / known markers as calibration anchors;
- pixel-to-stage homography for planar shortcuts;
- monocular depth as a fallible observation rather than geometry truth;
- cross-camera consistency checks;
- point-cloud / world-coordinate fusion;
- colour-based beam detection;
- automated mover sweeps;
- a sampled light map from pan/tilt to observed stage points;
- inverse lookup from desired stage point to pan/tilt;
- explicit calibration locks so normal control does not fight calibration.

### From Följe / followspot projects

- calibrate the reachable stage region rather than assume the whole image is valid;
- floor points are strong anchors because scenery and performers occlude beams;
- track in stage coordinates, then convert to fixture pan/tilt;
- preserve unrelated DMX attributes while taking control of only the dimensions required by tracking.

### From grandMA / PSN-style systems

- keep tracking as an external spatial signal;
- represent targets as world-space positions;
- the console/output engine consumes position rather than having to own the perception stack.

### From camera-calibration literature

- maintain intrinsics separately from extrinsics;
- use world reference points to align camera coordinates to stage coordinates;
- model uncertainty explicitly;
- prefer multiple observations over a single camera when geometry allows.

## MTRACK v0 components

```
Camera Registry
  - intrinsics
  - extrinsics / pose
  - FOV / resolution
  - confidence

Observation adapters
  - beam detector
  - object/person detector
  - depth estimator
  - manual observation
  - simulated 3D observation

Fusion
  - all observations converted to stage XYZ
  - confidence weighted
  - outlier rejection
  - source provenance retained

Fixture calibration
  - command pan/tilt
  - observe beam landing position
  - store CalibrationPoint
  - build LightMap
  - inverse query: XYZ -> pan/tilt

Prediction residual
  - predicted point from digital twin
  - observed point from cameras
  - residual vector + magnitude
  - later used for model correction / learning
```

## First boundary

MTRACK outputs semantic spatial facts:

```
Target(id=person_7, xyz=(...), confidence=.91)
BeamHit(fixture=17, xyz=(...), confidence=.84)
CalibrationModel(fixture=17, ...)
```

It does not output DMX directly and it does not invent a parallel semantic language. MTRACK publishes these observations to the shared X-ANALOGIA-X world model; that common engine decides whether they calibrate/refute a model or become part of an abstract control intention. Only then can the MDMX backend lower the validated intention to SemanticFrame/DMX.

## Safety / determinism

- MTRACK may fail, lose cameras or hallucinate depth.
- Deterministic DMX output must continue without depending on a live AI response.
- Every learned/estimated result carries confidence and provenance.
- Calibration and learning can propose model changes; activation should be explicit/versioned.
- Camera loss must degrade gracefully to 3D prediction / last validated calibration.

## Next gates

1. synthetic math tests;
2. manual 4-point stage calibration;
3. one camera + one fixture beam detection;
4. sampled light map;
5. inverse aiming;
6. two-camera fusion;
7. digital-twin prediction vs camera residual;
8. learned correction model;
9. live tracking target;
10. integration with the shared X-ANALOGIA-X ontology/DSL;
11. lowering validated abstract operations through the MDMX backend.

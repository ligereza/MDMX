# MTRACK data model — what exists and what may persist

## Ephemeral plane

Designed to disappear quickly:

- decoded video frames;
- image tensors;
- detector crops;
- transient pixel detections;
- short-lived tracker history;
- ephemeral track IDs;
- raw model activations.

Default policy: RAM only, bounded lifetime.

## Derived observation plane

May persist when useful for system quality:

- timestamp;
- source ID;
- observation kind;
- XYZ / ray / bounding geometry;
- confidence;
- calibration version used;
- model version used;
- fixture ID where relevant;
- prediction residual.

These records describe geometry/system behaviour rather than raw surveillance footage.

## Calibration plane

Persistent and versioned:

- camera intrinsics;
- lens distortion;
- camera extrinsics/pose;
- resolution and crop identity;
- PTZ/lens signature where relevant;
- coverage polygon/volume;
- RMS/reprojection validation metrics;
- fixture LightMaps;
- fixture pose/axis corrections;
- activation state and version.

## Rig/digital-twin plane

Persistent:

- fixture geometry;
- fixture semantic profile;
- stage/world geometry;
- named zones;
- camera locations;
- output patch;
- semantic group/order definitions.

## Secrets plane

Never committed to the rig repository:

- RTSP passwords;
- ONVIF passwords;
- venue network credentials.

Secrets belong in environment variables or an OS/service secret store.

## Learned-model plane

A learned model is not trusted merely because training converged.

```
training data
   -> candidate model
   -> held-out validation observations
   -> residual comparison
   -> human/policy approval
   -> ACTIVE
```

Store:

- model identifier/hash;
- training/calibration dataset IDs (not raw images by default);
- validation metrics;
- validity domain;
- predecessor model;
- activation decision.

## Identity boundary

MTRACK needs continuity of motion, not human identity. `track-17` means only 'the same short-lived geometric trajectory within this processing interval'. It must not silently become a named person, face embedding or persistent identity record.

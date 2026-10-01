# MTRACK research extraction

This file records concepts worth testing. It is not a claim that MTRACK implements every item.

## Projects reviewed

### SlyLED
Repository: https://github.com/SlyWombat/SlyLED

Useful concepts:
- 3D stage model;
- USB/RPi/Orange Pi camera nodes;
- beam detection;
- camera calibration;
- depth estimation;
- multi-camera point-cloud fusion;
- mover calibration;
- inverse aiming;
- local AI-assisted camera tuning.

Important license note: SlyLED is PolyForm Noncommercial. MTRACK must remain a clean-room implementation unless license compatibility is explicitly reviewed. We reuse architectural ideas and standard mathematical techniques, not their implementation.

### Följe
Repository: https://github.com/logflames/folje

Useful concepts:
- camera image as operator/tracking surface;
- calibration points defining a valid reachable region;
- stage-floor calibration;
- camera-space target -> pan/tilt;
- sACN output.

### DMX Followspot
Repository: https://github.com/sandinak/dmx-followspot

Useful concept:
- pass through normal lighting data while overriding only selected attributes such as pan/tilt.

### Fly My Fixtures
Repository: https://github.com/nhaun24/Fly-My-Fixtures

Useful concepts:
- multi-fixture fan-out;
- stage calibration;
- interpolation from calibrated stage coordinates to pan/tilt;
- global phase clock for synchronized movement.

### PTZ / sports camera calibration research

Useful concepts:
- pinhole intrinsics;
- pan/tilt/roll pose;
- focal length and principal point;
- radial/tangential distortion;
- world-reference alignment;
- temporal calibration for moving cameras.

## What appears genuinely interesting for MTRACK

Existing systems generally solve one of these:
- visualize a rig;
- calibrate a mover;
- track a person;
- transform XYZ into pan/tilt.

MTRACK should combine them into a persistent feedback model:

```
command
  -> predicted physical/visual consequence
  -> real observation
  -> residual
  -> model update
```

The long-term object is not "a camera followspot". It is a learned world/fixture model able to answer:

- what did this command visibly change?
- which fixture/channel caused that change?
- was the change visible from any sensor?
- do several different command sequences produce the same visible result?
- can this visual result be represented by a lower-dimensional rule?
- how confident are we in the prediction?
- what would produce a desired spatial/visual state?

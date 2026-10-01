# MTRACK — two Hikvision lab plan

Goal: prove that two ordinary security cameras can become temporary geometric sensors for MTRACK without recording video.

## Phase 0 — network only

- Put both cameras and the MTRACK computer on a network where the computer may reach the two camera IPs.
- Do not expose the cameras to the public Internet.
- Prefer dedicated ONVIF Media User credentials rather than administrator credentials.
- Start with each camera substream to reduce decode latency and bandwidth.
- Run `mtrack/tools/probe_cameras.py` and record only codec/resolution/FPS/health.

Gate: both sources must negotiate reliably for several minutes before any computer-vision work.

## Phase 1 — fixed-camera calibration

Use four or more points visible in both images and whose world/stage coordinates can be measured. Floor points are preferred initially because they define a stable plane.

Persist only:

```
intrinsics
lens distortion
camera world pose
calibration RMS error
coverage polygon
resolution
lens signature
```

Moving either camera, changing digital/optical zoom, changing resolution/crop, or changing a PTZ viewpoint invalidates the calibration unless the system can explicitly relocalize it.

## Phase 2 — prove geometry without AI

Pick one physical point visible to both cameras. Mark its pixel coordinate manually in each image. Convert both pixels into world rays and triangulate them.

Success criterion: reconstructed XYZ is close to the measured physical coordinate and the two closest rays have low separation.

This phase deliberately avoids object detection. If geometry is wrong, adding AI will only hide the error.

## Phase 3 — ephemeral target detection

Add a deliberately simple detector first, for example a high-contrast marker or bright coloured target. Detection produces:

```
pixel
timestamp
confidence
ephemeral_track_id
```

No face identity or persistent person identity is required.

Synchronize observations by timestamp before triangulation. If two frames are too far apart in time, do not fuse them as if they observed the same instant.

## Phase 4 — light observation

Use one moving head and a high-contrast beam/spot when practical. Sweep known Pan/Tilt values through a safe region and observe the landing point.

Build paired samples:

```
(pan16, tilt16) <-> observed XYZ
```

Use them to test both:

- forward prediction: Pan/Tilt -> expected BeamHit;
- inverse aiming: desired XYZ -> Pan/Tilt.

## Phase 5 — digital twin residual

For every validated test point:

```
predicted_xyz = digital_twin(command)
observed_xyz  = cameras(command)
residual      = observed_xyz - predicted_xyz
```

The residual is the learning signal. Do not modify the active model immediately; create a calibration/model candidate, validate it against held-out observations, then activate it.

## Practical limits

- Security cameras may add 100+ ms of encoder/network buffering; measure actual latency.
- Automatic exposure can make beam brightness appear nonlinear.
- IR/night mode can change image response and invalidate assumptions.
- Wide-angle lenses require distortion correction.
- Two cameras with a tiny baseline or similar viewing direction give weak depth triangulation.
- A target visible in only one camera is not automatically a 3D target.
- CCTV timestamps may not share a clock; timestamp gating is not a substitute for clock synchronization.
- PTZ cameras require viewpoint-aware calibration.

## What this proves

If these phases succeed, MTRACK has established the minimum chain:

```
existing CCTV
    -> calibrated rays
    -> common XYZ
    -> observed physical light consequence
    -> prediction residual
    -> candidate model correction
```

That is enough to begin learning fixture/world relationships without making the camera feed itself part of the stored show data.

# MTRACK — limits and failure boundaries

Status: normative design constraints for the MTRACK branch.

Every MTRACK capability must state what it knows, what it estimates and when it must refuse or degrade.

| Capability | Useful for | Hard limit / failure mode | Required fallback |
|---|---|---|---|
| RTSP/ONVIF CCTV ingest | Reuse venue cameras | Vendor quirks, disabled ONVIF, codec/latency differences | Manual RTSP config or disable source |
| Single-camera 2D tracking | Pixel-space motion | No metric depth from geometry alone | Floor intersection, known plane, depth model or another camera |
| Monocular learned depth | Approximate 3D cues | Scale ambiguity and hallucinated depth | Confidence reduction; never treat as ground truth |
| Homography | Pixel ↔ one plane | Valid only for the calibrated plane | Full camera extrinsics for non-planar points |
| Multi-camera fusion | Reduce occlusion/noise | Requires common coordinates and time alignment | Use strongest valid source, preserve provenance |
| Camera calibration | Pixel ↔ rays/world | Invalid after camera/lens/PTZ movement | Mark stale; recalibrate/relocalize |
| Passive trajectory calibration | Calibration without markers | Needs shared, diverse tracks and sufficient overlap | Keep previous validated calibration |
| Beam detection | Learn fixture landing points | Fails with saturation, haze, similar colors, occlusion | Change probe color/intensity/source or manual confirmation |
| LightMap interpolation | XYZ → Pan/Tilt without perfect physical model | Poor extrapolation outside sampled region | Reject outside trusted coverage |
| Parametric IK | Fast XYZ → Pan/Tilt | Depends on fixture pose/ranges/zero direction accuracy | Residual correction / sampled LightMap |
| Temporal prediction | Reduce visible tracking lag | Cannot predict abrupt motion reliably | Confidence decay + reacquisition |
| Attribute override | Let MTRACK aim while desk controls look | Conflicts if ownership is ambiguous | Explicit per-attribute lease and timeout |
| Digital twin prediction | Expected beam/visual result | Render is never identical to venue reality | Compare to cameras and retain residual |
| AI perception | Detect/estimate complex observations | False positives, domain shift, opaque uncertainty | Geometry/temporal gates and deterministic fallbacks |

## Non-negotiable invariants

1. Camera frames are observations, not truth.
2. Learned depth is never silently promoted to measured depth.
3. A calibration has a validity domain: source, resolution, lens state, pose and time/version.
4. An observation outside calibrated coverage cannot control a fixture as if it were validated.
5. MTRACK may own only explicitly leased semantic attributes.
6. Loss of MTRACK must not erase unrelated desk output.
7. Raw video/frame persistence is off by default.
8. No biometric identity is required for tracking; ephemeral track IDs are sufficient.
9. A learned calibration/model is a candidate until validated.
10. The deterministic MDMX output path must not block on live AI inference.

## Latency budget

Tracking quality depends on end-to-end latency, not camera FPS alone:

```
camera exposure/encode
 + network jitter
 + decode
 + detector
 + fusion
 + temporal estimator
 + semantic compile
 + DMX/network output
 + fixture motor response
 = visible tracking latency
```

Optimization should measure each component independently. Increasing camera FPS cannot compensate for a slow encoder, inference step or fixture motor.

## Coordinate-system rule

MTRACK has one canonical right-handed world/stage coordinate system. Every source adapter must transform observations into that frame before fusion. Camera pixel coordinates, depth coordinates, Capture-like 3D coordinates and fixture-local axes must not be mixed implicitly.

## Calibration activation rule

Calibration data follows:

```
COLLECT -> CANDIDATE -> VALIDATED -> ACTIVE -> STALE
```

No automatic learning path may jump directly from COLLECT to ACTIVE.

## Extrapolation rule

Interpolation inside a well-sampled calibration region may be trusted according to measured error. Extrapolation outside it must either be rejected or explicitly marked low-confidence. This follows the practical lesson from followspot systems that define a calibrated stage region rather than pretending the entire camera image is reachable.

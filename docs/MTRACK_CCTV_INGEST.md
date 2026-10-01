# MTRACK CCTV ingest

Status: experimental.

## Product idea

MTRACK should prefer existing venue CCTV when permission is available.

The deployment target is intentionally small:

```
venue CCTV VLAN / switch
          |
      one Ethernet
          |
      MTRACK host
          |
  +-------+-------+
  |       |       |
cam-a   cam-b   cam-n
  |       |       |
 RTSP / ONVIF read-only
          |
       RAM only
          |
  observations / XYZ
          |
   raw frame discarded
```

MTRACK is a temporary client of the venue camera infrastructure, not a replacement NVR.

## Access contract

1. MTRACK receives only the network reachability it needs.
2. Use a dedicated read-only/media credential, never the venue administrator account.
3. Prefer a dedicated VLAN or explicit ACL allowing MTRACK -> approved camera IPs only.
4. MTRACK does not reconfigure cameras unless a separately approved calibration procedure requires it.
5. No video recording by default.
6. No still-image persistence by default.
7. No facial recognition or identity database.
8. Frames are decoded in volatile memory, converted into geometric/visual observations and discarded.
9. Logs contain camera IDs and health/state, not credentials or raw imagery.
10. Derived calibration data may persist: camera pose, fixture response maps, confidence, XYZ observations and model residuals.

## Why ONVIF + RTSP

ONVIF is the interoperability/control plane: device services, media profiles and stream URIs. RTSP/RTP is the video plane.

MTRACK models the source independently of brand. Hikvision is the first adapter because two physical cameras are available for lab testing.

Prefer ONVIF Profile T for modern deployments. Profile T covers advanced IP video streaming including H.264/H.265 and ONVIF announced the phase-out of Profile S support in favour of Profile T in 2025.

## Hikvision lab

Hikvision documents ONVIF setup under Configuration -> Network -> Advanced Settings -> Integration Protocol. Enable ONVIF and create a dedicated ONVIF user.

A Media User is sufficient for real-time streaming, capability discovery and reading configuration on supported Hikvision cameras.

Hikvision documents these RTSP paths:

```
/Streaming/Channels/101  # camera/channel 1 main stream
/Streaming/Channels/102  # camera/channel 1 sub stream
```

Ports are configurable and belong in MTRACK configuration rather than being assumed globally.

For analysis, start with the substream. Calibration can request the main stream later when extra spatial resolution is actually useful.

## Two-camera first experiment

### A — connectivity

- Give each camera a stable IP or DHCP reservation.
- Enable ONVIF if the model requires it.
- Create a dedicated Media User.
- Copy mtrack/config/hikvision-two-cameras.example.toml and set the two camera hosts.
- Store credentials only in environment variables.
- Run mtrack/tools/probe_cameras.py.

Success means both streams negotiate and return codec/resolution/FPS. The probe writes no video.

### B — common world coordinates

Each stream becomes an ObservationSource. Calibrate both cameras against known stage/world points so detections from either source can be expressed as the same XYZ coordinates.

### C — confidence instead of blind averaging

- cameras with glare, occlusion or poor view receive lower confidence;
- two agreeing observations increase confidence;
- a far inconsistent observation can be rejected;
- source provenance remains attached to every fused observation.

### D — closed loop

```
MDMX sends PAN/TILT
       |
       v
digital twin predicts BeamHit XYZ
       |
       v
cam-a observation ---+
                     +--> fused BeamHit XYZ
cam-b observation ---+
       |
       v
residual = observed - predicted
       |
       v
fixture calibration / learned correction
```

The first learned object is therefore not a person identity model. It is the relationship between fixture command, stage geometry and visible consequence.

## Current implementation

- ObservationSource abstracts CCTV, ONVIF, MDMX-owned cameras, simulators and external metadata.
- PrivacyPolicy defaults to no video/frame persistence and no biometric identification.
- HikvisionCamera implements Hikvision RTSP path generation.
- credentials come from environment variables rather than committed files.
- probe_camera uses ffprobe only to negotiate/read stream metadata; it does not record media.
- stream URLs are redacted before display.

## Venue network recommendation

One physical Ethernet uplink is possible when the venue exposes CCTV through a permitted VLAN/trunk or routed interface. MTRACK should not become a bridge between the CCTV and lighting networks.

The preferred topology is a dual-homed or VLAN-aware endpoint with firewall rules: MTRACK may initiate traffic to approved camera addresses, while CCTV cannot initiate arbitrary traffic into the show network.

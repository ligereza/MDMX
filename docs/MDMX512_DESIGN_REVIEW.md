# MDMX512 — design review after research and prototype

Status: EXPERIMENTAL / NOT PRODUCTION READY

This document records the design after several rounds of comparison against Titan personalities, media-server control, DMX transport behaviour and the executable prototype.

## 1. Core thesis

MDMX512 is not "512 compressed DMX channels".

It is one reserved 512-slot control universe whose slots describe a small number of **operators** over a rig model already stored in MDMX.

The receiver expands those operators into ordinary DMX/Art-Net/sACN universes.

```
Titan
  |
  | one control universe
  v
MDMX512 personality
  |
  v
31 operator lanes
  |
  +---- rig registry (MVR/GDTF/manual)
  |
  v
expansion engine
  |
  +--> U1
  +--> U2
  +--> U3
  ...
  +--> UN
```

The output universe count is not mathematically unlimited. The useful scaling comes from shared structure: groups, ordering, geometry, presets and parametric functions.

## 2. Existing precedent validates the control model

Avolites already controls external media servers through fixture personalities. Ai supports Art-Net/DMX modes where channels mean things such as media selection, playback speed, X/Y/Z rotation, image position and intensity. Catalyst historically used a similar per-layer fixture model.

Resolume also maps DMX channels to higher-level operations; one DMX channel can select among many clips.

Therefore "lighting desk emits DMX parameters that an external engine interprets" is established practice. MDMX512 applies the pattern to lighting expansion rather than media playback.

Research references:

- https://www.avolites.com/Portals/0/downloads/Software/Ai/V8%20Training%20Guides/16-Lighting-Console-Control.pdf
- https://www.avolites.com/Portals/0/downloads/Software/Ai/AI_Man_V8.pdf
- https://resolume.com/support/en/dmx-shortcuts
- https://manual.avolites.com/docs/fixture-personalities/
- https://manual.avolites.com/docs/controlling-fixtures/

## 3. Hard information limit

One universe contains 512 eight-bit slots.

It cannot describe an arbitrary independent state for an unlimited number of physical slots.

Example:

- 1000 independent dimmers require 1000 independent values if no relationship is known.
- But 1000 dimmers in a linear ramp can be represented by group + start + end.
- 1000 dimmers following one sine wave can be represented by group + centre + amplitude + speed + phase/spread.
- 1000 fixtures using a stored look can be represented by one preset ID.

MDMX512 is therefore **model-based expansion**, not general lossless compression.

## 4. Why the receiver must know the rig

The control plane should not resend fixture personalities and patch information continuously.

MDMX stores a persistent registry:

- fixture ID;
- fixture type/profile;
- universe and DMX address;
- semantic channel map;
- group memberships;
- fixture order;
- optional X/Y/Z and orientation;
- calibration and limits.

MVR/GDTF are natural import sources. Manual configuration remains useful for early testing.

The control universe then references group IDs and semantic attributes rather than physical slots.

## 5. Titan integration: one super-fixture with cells

Titan supports multicell/subfixture personalities.

The experimental Avolites personality in this repository uses this structure:

```
MDMX512
|
+-- Master / global area: 16 DMX slots
|
+-- Lane 01: 16 slots
+-- Lane 02: 16 slots
...
+-- Lane 31: 16 slots
```

This naturally produces four modes:

| Mode | Operator lanes |
|---|---:|
| 64 DMX | 3 |
| 128 DMX | 7 |
| 256 DMX | 15 |
| 512 DMX | 31 |

The generated experimental personality is:

`fixtures/avolites/MDMX_MDMX512_EXPERIMENTAL.d4`

It is structurally validated by CI but has **not yet been validated inside Titan Simulator**, so it must not be considered a finished personality.

## 6. Current 16-byte lane

```
0      Enable
1      Operator
2      Attribute
3      Flags
4..5   Target Group ID
6..7   P0
8..9   P1
10..11 P2
12..13 P3
14..15 P4
```

All wide values use the normal DMX coarse/fine ordering.

The operator decides what P0..P4 mean.

Examples:

### SET

```
group = 12
attribute = DIMMER
P0 = 80%
```

Result: all compatible fixtures in group 12 receive 80% dimmer.

### RAMP

```
group = 12
attribute = PAN
P0 = -40 deg
P1 = +40 deg
```

Result: each fixture gets a different pan according to its order.

### WAVE

```
group = 12
attribute = DIMMER
P0 = centre
P1 = amplitude
P2 = speed
P3 = spread
P4 = phase
```

Result: MDMX evaluates the wave locally and continuously.

## 7. Proposed operator family

V0 currently implements SET, RAMP and WAVE only.

Candidate next operators:

- SYM_RAMP — centre-out / outside-in fan.
- CHASE — low/high values, width, speed, phase.
- STEP — indexed steps across ordered fixtures.
- GRADIENT — semantic colour interpolation.
- MIRROR — derive one selection from another.
- PRESET — recall a stored recipe/scene by ID.
- LOOK_AT — calculate pan/tilt from fixture geometry and target ID.
- OFFSET — add a relative value to an existing semantic result.
- SCALE — multiply an existing result.
- MASK — select odd/even/range/pattern subsets.

The operator set should remain small. New operators should only be added when they produce meaningful expansion or reduce console-side complexity.

## 8. Titan fan/effects cannot be magically preserved

This is a critical limitation.

Titan's native fan/shape engine computes per-fixture values for fixtures that Titan itself knows individually.

If 100 real fixtures are hidden behind one MDMX512 virtual fixture, Titan cannot output those 100 already-computed values through a single abstract channel.

Therefore MDMX512 exposes **fan/effect parameters themselves**:

- group;
- attribute;
- operation;
- start/end;
- size;
- speed;
- phase/spread;
- order/direction.

Titan stores, cues, fades and plays back these parameters. MDMX performs the hidden per-fixture calculation.

This is closer to controlling a media-server layer than to repatching normal fixtures.

## 9. Declarative snapshot, not event commands

DMX is a continuously repeated one-way stream. A full 512-slot frame is roughly 23 ms, about 44 Hz maximum, and standard DMX has no application-level acknowledgement or CRC.

An event protocol such as:

```
if channel changes -> run command once
```

is fragile.

MDMX512 instead treats every input frame as a current desired state:

```
Lane 3 = WAVE(group 12, dimmer, ...)
```

The receiver can repeatedly evaluate the same snapshot without side effects. If one packet is lost, the next one restores the same desired state.

For operations that genuinely need an edge/reset, a future per-lane epoch/generation field can make repeated frames idempotent.

## 10. Local timebase is essential

Fast effects should not require Titan to transmit every derived fixture value.

Titan sends parameters such as:

```
speed = 1.2 Hz
spread = 360 deg
phase = 0
```

MDMX runs the oscillator locally.

This is one of the main sources of expansion and also avoids tying output smoothness to the control-universe refresh rate.

A future synchronization design should define whether effect phase is referenced to:

- local monotonic clock;
- show timecode;
- externally supplied sync epoch;
- cue start generation.

## 11. Multiple lanes need composition rules

Two lanes may target the same group and attribute.

The engine therefore needs explicit composition semantics.

Candidate modes:

- REPLACE/LTP — highest priority or latest configured lane wins;
- HTP/MAX — useful for intensity;
- ADD — offsets/modulation;
- MULTIPLY — master/envelope;
- MIN/MAX;
- MASK.

These rules must be deterministic and independent of evaluation order wherever possible.

A recommended pipeline is:

```
BASE
  -> REPLACE layer
  -> ADD/OFFSET
  -> MULTIPLY/MASTER
  -> LIMIT/CALIBRATION
  -> fixture encoding
  -> physical DMX
```

## 12. Input transport

First implementation recommendation:

```
Titan -> Art-Net or sACN -> MDMX host/Raspberry Pi
```

Do not build physical DMX input first.

Reasons:

- no extra receiver hardware;
- direct full-universe snapshots;
- easier capture/debugging;
- Art-Net has a sequence field for detecting/reordering packets when enabled;
- output can remain independent from the control universe.

Physical DMX input can be added later without changing the 512-slot representation.

Reference:
https://art-net.org.uk/downloads/art-net.pdf

## 13. Output transport

The control plane and output plane are separate.

Possible expansion targets:

- local MDMX-OUT4 via FRAMESET_V1;
- Art-Net universes;
- sACN universes;
- multiple physical MDMX output nodes.

For multi-universe IP output, synchronization should be evaluated explicitly rather than assuming UDP arrival order equals visual atomicity.

## 14. Failure behaviour

Recommended defaults:

- invalid protocol version -> reject frame;
- unarmed control frame -> no semantic output;
- unknown group -> ignore lane + report diagnostic;
- unsupported attribute on a fixture -> skip that fixture + diagnostic;
- stale control source -> HOLD last valid semantic state initially;
- invalid operator/parameters -> reject that lane, not the entire rig;
- configuration mismatch -> visible warning in MDMX UI/API.

No blackouts should be invented implicitly unless configured.

## 15. What "limitless universes" should mean

Avoid the claim literally.

A better statement is:

> One MDMX512 control universe can drive an output space much larger than one universe when the output is derivable from shared semantic operations and a stored rig model.

Practical limits are:

- 31 simultaneous operator lanes in the current 512 mode;
- CPU cost of expansion;
- network/output bandwidth;
- number of registered fixtures;
- output node capacity;
- complexity/entropy of the desired look.

If a show requires thousands of completely independent values at once, more control information is required.

## 16. Prototype evidence currently in repo

`prototype/mdmx512/protocol.py` implements:

- exact 512-slot snapshots;
- 31 fixed operator lanes;
- 16-bit coarse/fine parameters;
- SET;
- RAMP;
- WAVE;
- fixture registry;
- groups;
- expansion to arbitrary output universes.

Tests prove:

1. 512-slot encode/decode round trip.
2. One 16-byte lane expands to 10 independent dimmers in ten 51-channel fixtures.
3. One lane can target a group spanning more than one output universe.
4. Global master scales generated dimmer values.
5. The experimental Avolites .d4 is valid XML and contains the expected 64/128/256/512 modes and 31 cells in 512 mode.

These tests validate the software model, **not compatibility with Titan itself**.

## 17. Next decisive experiment

The next experiment should be extremely small:

1. Install the experimental MDMX512 .d4 in Titan Simulator.
2. Patch the 64-channel / 3-lane mode.
3. Send its universe as Art-Net to a laptop/Raspberry Pi.
4. Capture all 64 values.
5. Verify that Arm, Version, Profile, Group, Operator and P0/P1 are emitted as expected.
6. Use Lane 1 = RAMP / DIMMER / Group 1.
7. Expand it into 10 fake fixtures.
8. Observe the 10 resulting dimmer values in a universe monitor.
9. Record a Titan cue and fade P0/P1.
10. Confirm the expanded ten fixtures follow smoothly.

If that works, the architecture has crossed from a software thought experiment into a console-compatible control protocol.

from __future__ import annotations

from statistics import median

from .model import Observation3D, Vec3


def _weighted_mean(observations: list[Observation3D]) -> Vec3:
    total = sum(max(0.0, o.confidence) for o in observations)
    if total <= 0:
        raise ValueError("at least one observation must have positive confidence")

    return Vec3(
        sum(o.point.x * max(0.0, o.confidence) for o in observations) / total,
        sum(o.point.y * max(0.0, o.confidence) for o in observations) / total,
        sum(o.point.z * max(0.0, o.confidence) for o in observations) / total,
    )


def fuse_observations(
    observations: list[Observation3D],
    *,
    outlier_factor: float = 3.0,
    floor_m: float = 0.05,
) -> Observation3D:
    """Fuse world-space observations with simple robust rejection.

    MTRACK adapters must transform camera/depth detections into the same
    stage coordinate system before calling this function.
    """
    if not observations:
        raise ValueError("observations cannot be empty")

    if len(observations) == 1:
        return observations[0]

    first = _weighted_mean(observations)
    distances = [o.point.distance_to(first) for o in observations]
    med = median(distances)
    threshold = max(floor_m, med * outlier_factor)

    kept = [
        o for o, distance in zip(observations, distances)
        if distance <= threshold
    ]
    if not kept:
        kept = observations

    point = _weighted_mean(kept)
    confidence = min(
        1.0,
        sum(max(0.0, min(1.0, o.confidence)) for o in kept) / len(kept),
    )

    return Observation3D(
        source_id="+".join(sorted(o.source_id for o in kept)),
        point=point,
        confidence=confidence,
        timestamp_s=max(o.timestamp_s for o in kept),
        kind=kept[0].kind if all(o.kind == kept[0].kind for o in kept) else "fused",
    )

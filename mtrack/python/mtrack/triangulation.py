from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from .camera_model import WorldRay
from .model import Vec3


@dataclass(frozen=True)
class TriangulationResult:
    point: Vec3
    ray_separation: float
    geometry_strength: float


def _dot(a: Vec3, b: Vec3) -> float:
    return a.x * b.x + a.y * b.y + a.z * b.z


def triangulate_rays(
    first: WorldRay,
    second: WorldRay,
    *,
    min_geometry_strength: float = 1e-3,
) -> TriangulationResult:
    """Return midpoint of the closest points on two forward camera rays.

    geometry_strength is sin(angle)^2 for normalized rays. Values near zero
    mean almost-parallel rays and therefore unreliable depth.
    """
    d1, d2 = first.direction, second.direction
    w0 = first.origin - second.origin

    a = _dot(d1, d1)
    b = _dot(d1, d2)
    c = _dot(d2, d2)
    d = _dot(d1, w0)
    e = _dot(d2, w0)

    denom = a * c - b * b
    strength = denom / max(a * c, 1e-12)
    if strength < min_geometry_strength:
        raise ValueError("camera rays are too parallel for reliable triangulation")

    t1 = (b * e - c * d) / denom
    t2 = (a * e - b * d) / denom
    if t1 < 0 or t2 < 0:
        raise ValueError("triangulated point lies behind a camera")

    p1 = first.origin + d1.scale(t1)
    p2 = second.origin + d2.scale(t2)
    midpoint = (p1 + p2).scale(0.5)
    separation = p1.distance_to(p2)

    return TriangulationResult(
        point=midpoint,
        ray_separation=separation,
        geometry_strength=max(0.0, min(1.0, strength)),
    )

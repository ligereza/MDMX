from __future__ import annotations

from dataclasses import dataclass

from .model import Vec3


@dataclass(frozen=True)
class CoveragePolygon:
    """Trusted planar calibration region in MTRACK world coordinates."""

    vertices_xy: tuple[tuple[float, float], ...]
    z_reference: float = 0.0

    def __post_init__(self) -> None:
        if len(self.vertices_xy) < 3:
            raise ValueError("coverage polygon needs at least three vertices")

    def contains_xy(self, point: Vec3) -> bool:
        x, y = point.x, point.y
        inside = False
        pts = self.vertices_xy
        j = len(pts) - 1
        for idx, (xi, yi) in enumerate(pts):
            xj, yj = pts[j]
            crosses = (yi > y) != (yj > y)
            if crosses:
                x_hit = (xj - xi) * (y - yi) / (yj - yi) + xi
                if x < x_hit:
                    inside = not inside
            j = idx
        return inside

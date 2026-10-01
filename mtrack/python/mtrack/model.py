from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class Vec3:
    x: float
    y: float
    z: float

    def __add__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def scale(self, k: float) -> "Vec3":
        return Vec3(self.x * k, self.y * k, self.z * k)

    def distance_to(self, other: "Vec3") -> float:
        d = self - other
        return sqrt(d.x * d.x + d.y * d.y + d.z * d.z)


@dataclass(frozen=True)
class Observation3D:
    source_id: str
    point: Vec3
    confidence: float
    timestamp_s: float
    kind: str = "generic"


@dataclass(frozen=True)
class CalibrationPoint:
    pan16: int
    tilt16: int
    stage: Vec3
    confidence: float = 1.0


@dataclass(frozen=True)
class Residual:
    predicted: Vec3
    observed: Vec3
    delta: Vec3
    magnitude: float
    confidence: float

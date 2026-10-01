from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Tuple

from .model import Vec3


Mat3 = Tuple[
    Tuple[float, float, float],
    Tuple[float, float, float],
    Tuple[float, float, float],
]


@dataclass(frozen=True)
class Pixel:
    x: float
    y: float


@dataclass(frozen=True)
class CameraIntrinsics:
    fx: float
    fy: float
    cx: float
    cy: float
    width: int
    height: int
    k1: float = 0.0
    k2: float = 0.0
    p1: float = 0.0
    p2: float = 0.0
    k3: float = 0.0

    def __post_init__(self) -> None:
        if self.fx <= 0 or self.fy <= 0:
            raise ValueError("fx/fy must be positive")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("image dimensions must be positive")


@dataclass(frozen=True)
class CameraPose:
    """Camera pose in MTRACK world coordinates.

    rotation_wc maps a vector expressed in camera coordinates into world
    coordinates. position is the camera optical centre in world coordinates.
    """

    position: Vec3
    rotation_wc: Mat3


@dataclass(frozen=True)
class CameraCalibration:
    source_id: str
    intrinsics: CameraIntrinsics
    pose: CameraPose
    rms_error_px: float
    confidence: float

    def __post_init__(self) -> None:
        if not self.source_id:
            raise ValueError("source_id cannot be empty")
        if self.rms_error_px < 0:
            raise ValueError("rms_error_px cannot be negative")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0,1]")


@dataclass(frozen=True)
class WorldRay:
    origin: Vec3
    direction: Vec3


def _mat_vec(m: Mat3, v: Vec3) -> Vec3:
    return Vec3(
        m[0][0] * v.x + m[0][1] * v.y + m[0][2] * v.z,
        m[1][0] * v.x + m[1][1] * v.y + m[1][2] * v.z,
        m[2][0] * v.x + m[2][1] * v.y + m[2][2] * v.z,
    )


def _transpose(m: Mat3) -> Mat3:
    return (
        (m[0][0], m[1][0], m[2][0]),
        (m[0][1], m[1][1], m[2][1]),
        (m[0][2], m[1][2], m[2][2]),
    )


def _normalize(v: Vec3) -> Vec3:
    n = sqrt(v.x * v.x + v.y * v.y + v.z * v.z)
    if n <= 1e-12:
        raise ValueError("zero-length direction")
    return Vec3(v.x / n, v.y / n, v.z / n)


def _distort(x: float, y: float, i: CameraIntrinsics) -> tuple[float, float]:
    r2 = x * x + y * y
    radial = 1.0 + i.k1 * r2 + i.k2 * r2 * r2 + i.k3 * r2 * r2 * r2
    dx = 2.0 * i.p1 * x * y + i.p2 * (r2 + 2.0 * x * x)
    dy = i.p1 * (r2 + 2.0 * y * y) + 2.0 * i.p2 * x * y
    return x * radial + dx, y * radial + dy


def _undistort(xd: float, yd: float, i: CameraIntrinsics) -> tuple[float, float]:
    x, y = xd, yd
    for _ in range(8):
        r2 = x * x + y * y
        radial = 1.0 + i.k1 * r2 + i.k2 * r2 * r2 + i.k3 * r2 * r2 * r2
        if abs(radial) <= 1e-12:
            raise ValueError("invalid distortion model")
        dx = 2.0 * i.p1 * x * y + i.p2 * (r2 + 2.0 * x * x)
        dy = i.p1 * (r2 + 2.0 * y * y) + 2.0 * i.p2 * x * y
        x = (xd - dx) / radial
        y = (yd - dy) / radial
    return x, y


def pixel_to_world_ray(cal: CameraCalibration, pixel: Pixel) -> WorldRay:
    i = cal.intrinsics
    xd = (pixel.x - i.cx) / i.fx
    yd = (pixel.y - i.cy) / i.fy
    x, y = _undistort(xd, yd, i)
    camera_ray = _normalize(Vec3(x, y, 1.0))
    return WorldRay(
        origin=cal.pose.position,
        direction=_normalize(_mat_vec(cal.pose.rotation_wc, camera_ray)),
    )


def world_to_pixel(cal: CameraCalibration, point: Vec3) -> Pixel:
    rel = point - cal.pose.position
    camera = _mat_vec(_transpose(cal.pose.rotation_wc), rel)
    if camera.z <= 1e-9:
        raise ValueError("point is behind camera")

    x = camera.x / camera.z
    y = camera.y / camera.z
    xd, yd = _distort(x, y, cal.intrinsics)
    return Pixel(
        cal.intrinsics.fx * xd + cal.intrinsics.cx,
        cal.intrinsics.fy * yd + cal.intrinsics.cy,
    )


def intersect_z_plane(ray: WorldRay, z: float = 0.0) -> Vec3:
    if abs(ray.direction.z) <= 1e-12:
        raise ValueError("ray is parallel to requested plane")
    t = (z - ray.origin.z) / ray.direction.z
    if t < 0:
        raise ValueError("plane intersection is behind camera")
    return ray.origin + ray.direction.scale(t)

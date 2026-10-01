import unittest

from mtrack.camera_model import (
    CameraCalibration,
    CameraIntrinsics,
    CameraPose,
    pixel_to_world_ray,
    world_to_pixel,
)
from mtrack.model import Vec3
from mtrack.triangulation import triangulate_rays


IDENTITY = (
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
)


def camera(source_id: str, x: float) -> CameraCalibration:
    return CameraCalibration(
        source_id=source_id,
        intrinsics=CameraIntrinsics(1000, 1000, 960, 540, 1920, 1080),
        pose=CameraPose(Vec3(x, 0, 0), IDENTITY),
        rms_error_px=0.5,
        confidence=1.0,
    )


class TriangulationTests(unittest.TestCase):
    def test_two_cameras_reconstruct_world_point(self):
        target = Vec3(0.2, 0.4, 6.0)
        ca = camera("a", -1.0)
        cb = camera("b", 1.0)
        ra = pixel_to_world_ray(ca, world_to_pixel(ca, target))
        rb = pixel_to_world_ray(cb, world_to_pixel(cb, target))
        result = triangulate_rays(ra, rb)
        self.assertLess(result.point.distance_to(target), 1e-6)
        self.assertLess(result.ray_separation, 1e-6)
        self.assertGreater(result.geometry_strength, 0.01)

    def test_near_parallel_rays_are_rejected(self):
        ca = camera("a", 0.0)
        cb = camera("b", 0.001)
        target = Vec3(0, 0, 1000)
        ra = pixel_to_world_ray(ca, world_to_pixel(ca, target))
        rb = pixel_to_world_ray(cb, world_to_pixel(cb, target))
        with self.assertRaises(ValueError):
            triangulate_rays(ra, rb, min_geometry_strength=1e-4)


if __name__ == "__main__":
    unittest.main()

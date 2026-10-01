import unittest

from mtrack.authority import AttributeLease, Authority, resolve_attribute
from mtrack.camera_model import (
    CameraCalibration,
    CameraIntrinsics,
    CameraPose,
    Pixel,
    intersect_z_plane,
    pixel_to_world_ray,
    world_to_pixel,
)
from mtrack.coverage import CoveragePolygon
from mtrack.evidence import PassiveCalibrationBuffer, PassiveCalibrationSample
from mtrack.model import Vec3
from mtrack.quality import ConfidenceInputs, effective_confidence
from mtrack.temporal import AlphaBetaTracker


IDENTITY = (
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
)


class GeometryTests(unittest.TestCase):
    def calibration(self):
        return CameraCalibration(
            source_id="cam-a",
            intrinsics=CameraIntrinsics(
                fx=1000.0, fy=1000.0, cx=960.0, cy=540.0,
                width=1920, height=1080,
            ),
            pose=CameraPose(Vec3(0.0, 0.0, 2.0), IDENTITY),
            rms_error_px=0.5,
            confidence=0.95,
        )

    def test_world_pixel_round_trip(self):
        cal = self.calibration()
        point = Vec3(1.0, 0.5, 5.0)
        pixel = world_to_pixel(cal, point)
        ray = pixel_to_world_ray(cal, pixel)
        self.assertGreater(ray.direction.z, 0)
        # The original point must lie on the generated ray.
        t = (point.z - ray.origin.z) / ray.direction.z
        reconstructed = ray.origin + ray.direction.scale(t)
        self.assertLess(reconstructed.distance_to(point), 1e-6)

    def test_plane_intersection(self):
        cal = CameraCalibration(
            source_id="down",
            intrinsics=CameraIntrinsics(1000, 1000, 500, 500, 1000, 1000),
            pose=CameraPose(
                Vec3(0, 0, 5),
                ((1, 0, 0), (0, -1, 0), (0, 0, -1)),
            ),
            rms_error_px=1,
            confidence=1,
        )
        hit = intersect_z_plane(pixel_to_world_ray(cal, Pixel(500, 500)), 0)
        self.assertLess(hit.distance_to(Vec3(0, 0, 0)), 1e-9)

    def test_coverage_polygon(self):
        area = CoveragePolygon(((0, 0), (10, 0), (10, 5), (0, 5)))
        self.assertTrue(area.contains_xy(Vec3(3, 2, 0)))
        self.assertFalse(area.contains_xy(Vec3(12, 2, 0)))


class TemporalAndAuthorityTests(unittest.TestCase):
    def test_tracker_predicts_forward(self):
        tracker = AlphaBetaTracker(alpha=1.0, beta=1.0)
        tracker.update(Vec3(0, 0, 0), 0.0, 1.0)
        tracker.update(Vec3(1, 0, 0), 1.0, 1.0)
        predicted = tracker.predict(2.0)
        self.assertAlmostEqual(predicted.x, 2.0)

    def test_unowned_attributes_pass_through(self):
        lease = AttributeLease(
            fixture_id=7,
            attributes=frozenset({"pan", "tilt"}),
            authority=Authority.MTRACK_OVERRIDE,
        )
        self.assertEqual(resolve_attribute(90, 10, lease, "dimmer", 1.0), 90)
        self.assertEqual(resolve_attribute(90, 10, lease, "pan", 1.0), 10)

    def test_expired_lease_releases_control(self):
        lease = AttributeLease(
            fixture_id=7,
            attributes=frozenset({"pan"}),
            authority=Authority.MTRACK_OVERRIDE,
            expires_at_s=2.0,
        )
        self.assertEqual(resolve_attribute(77, 12, lease, "pan", 3.0), 77)


class EvidenceAndConfidenceTests(unittest.TestCase):
    def test_passive_calibration_rejects_degenerate_track(self):
        buf = PassiveCalibrationBuffer()
        for i in range(25):
            buf.add(PassiveCalibrationSample("cam-a", "t", 100, 100, i * 0.2))
        quality = buf.quality()
        self.assertFalse(quality.ready)
        self.assertIn("degenerate", quality.reason)

    def test_passive_calibration_accepts_diverse_track(self):
        buf = PassiveCalibrationBuffer()
        for i in range(25):
            buf.add(PassiveCalibrationSample("cam-a", "t", 10 * i, 5 * i, i * 0.2))
        self.assertTrue(buf.quality().ready)

    def test_confidence_decays_and_coverage_gates(self):
        fresh = effective_confidence(
            ConfidenceInputs(1, 1, 1, age_ms=0, inside_coverage=True)
        )
        old = effective_confidence(
            ConfidenceInputs(1, 1, 1, age_ms=500, inside_coverage=True)
        )
        outside = effective_confidence(
            ConfidenceInputs(1, 1, 1, age_ms=0, inside_coverage=False)
        )
        self.assertEqual(fresh, 1.0)
        self.assertLess(old, fresh)
        self.assertEqual(outside, 0.0)


if __name__ == "__main__":
    unittest.main()

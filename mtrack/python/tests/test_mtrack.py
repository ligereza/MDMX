import unittest

from mtrack import (
    CalibrationPoint,
    LightMap,
    Observation3D,
    Vec3,
    fuse_observations,
    residual,
)


class MTrackTests(unittest.TestCase):
    def test_lightmap_exact_anchor(self):
        lm = LightMap([
            CalibrationPoint(1000, 2000, Vec3(0, 0, 0)),
            CalibrationPoint(50000, 40000, Vec3(10, 0, 0)),
        ])
        aim = lm.aim(Vec3(0, 0, 0))
        self.assertEqual((aim.pan16, aim.tilt16), (1000, 2000))

    def test_lightmap_interpolates_between_samples(self):
        lm = LightMap([
            CalibrationPoint(0, 10000, Vec3(0, 0, 0)),
            CalibrationPoint(65535, 10000, Vec3(10, 0, 0)),
        ])
        aim = lm.aim(Vec3(5, 0, 0))
        self.assertTrue(32000 <= aim.pan16 <= 33535)
        self.assertEqual(aim.tilt16, 10000)

    def test_multicamera_fusion_rejects_far_outlier(self):
        observations = [
            Observation3D("cam-a", Vec3(1.00, 2.00, 0.0), 0.9, 1.0, "beam"),
            Observation3D("cam-b", Vec3(1.04, 1.98, 0.0), 0.8, 1.0, "beam"),
            Observation3D("bad-depth", Vec3(20.0, 20.0, 8.0), 0.2, 1.0, "beam"),
        ]
        fused = fuse_observations(observations, outlier_factor=1.5)
        self.assertLess(fused.point.distance_to(Vec3(1.02, 1.99, 0.0)), 0.1)
        self.assertNotIn("bad-depth", fused.source_id)

    def test_prediction_residual(self):
        obs = Observation3D("cam-a", Vec3(1, 2, 3), 0.75, 1.0, "beam")
        r = residual(Vec3(1, 2, 2), obs)
        self.assertEqual(r.delta, Vec3(0, 0, 1))
        self.assertEqual(r.magnitude, 1.0)
        self.assertEqual(r.confidence, 0.75)


if __name__ == "__main__":
    unittest.main()

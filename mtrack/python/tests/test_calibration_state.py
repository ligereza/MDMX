import unittest

from mtrack.calibration_state import CalibrationRecord, CalibrationState
from mtrack.model import Observation3D, Vec3
from mtrack.sync import synchronize_observations


class CalibrationLifecycleTests(unittest.TestCase):
    def test_candidate_cannot_jump_directly_to_active(self):
        record = CalibrationRecord("cal-1", "cam-a", CalibrationState.COLLECT)
        candidate = record.propose(
            rms_error_px=0.8,
            sample_count=100,
            resolution=(1920, 1080),
            lens_signature="fixed",
        )
        with self.assertRaises(ValueError):
            candidate.activate()

    def test_validated_candidate_can_activate(self):
        record = CalibrationRecord("cal-1", "cam-a", CalibrationState.COLLECT)
        active = (
            record.propose(
                rms_error_px=0.8,
                sample_count=100,
                resolution=(1920, 1080),
                lens_signature="fixed",
            )
            .validate(max_rms_error_px=1.0)
            .activate()
        )
        self.assertEqual(active.state, CalibrationState.ACTIVE)

    def test_resolution_change_marks_calibration_stale(self):
        record = CalibrationRecord(
            "cal-1",
            "cam-a",
            CalibrationState.ACTIVE,
            rms_error_px=0.5,
            sample_count=100,
            resolution=(1920, 1080),
            lens_signature="zoom-1",
        )
        stale = record.verify_runtime_identity(
            resolution=(1280, 720),
            lens_signature="zoom-1",
        )
        self.assertEqual(stale.state, CalibrationState.STALE)


class SyncTests(unittest.TestCase):
    def test_sync_window_drops_old_observation(self):
        observations = [
            Observation3D("a", Vec3(0, 0, 0), 1, 10.000),
            Observation3D("b", Vec3(0, 0, 0), 1, 10.030),
            Observation3D("old", Vec3(0, 0, 0), 1, 9.500),
        ]
        window = synchronize_observations(observations, max_skew_ms=50)
        self.assertEqual({o.source_id for o in window.observations}, {"a", "b"})
        self.assertLessEqual(window.span_ms, 50.0)


if __name__ == "__main__":
    unittest.main()

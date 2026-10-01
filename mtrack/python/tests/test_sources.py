import os
from pathlib import Path
import tempfile
import unittest

from mtrack.camera_config import load_hikvision_config
from mtrack.hikvision import HikvisionCamera
from mtrack.sources import ObservationSource, PrivacyPolicy, SourceKind


class SourceTests(unittest.TestCase):
    def test_default_privacy_is_ephemeral(self):
        policy = PrivacyPolicy()
        self.assertFalse(policy.persist_video)
        self.assertFalse(policy.persist_frames)
        self.assertFalse(policy.biometric_identification)

    def test_hikvision_substream_path(self):
        source = ObservationSource("cam-a", SourceKind.ONVIF, "10.0.0.10")
        camera = HikvisionCamera(source, channel=1, stream="sub")
        self.assertEqual(camera.rtsp_path, "/Streaming/Channels/102")

    def test_uri_encodes_credentials_and_redacts_logs(self):
        source = ObservationSource("cam-a", SourceKind.ONVIF, "10.0.0.10")
        camera = HikvisionCamera(source, stream="main", rtsp_port=8554)
        uri = camera.rtsp_uri("m track", "a@b:c")
        self.assertIn("m%20track", uri)
        self.assertIn("a%40b%3Ac", uri)
        redacted = camera.redacted_rtsp_uri("m track")
        self.assertNotIn("a@b:c", redacted)
        self.assertIn("***", redacted)

    def test_config_reads_secrets_only_from_environment(self):
        config = """
[[camera]]
id = "cam-a"
host = "192.0.2.10"
credential_env_prefix = "MTRACK_TEST_A"
stream = "sub"
"""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "cams.toml"
            path.write_text(config, encoding="utf-8")
            old_user = os.environ.get("MTRACK_TEST_A_USER")
            old_pass = os.environ.get("MTRACK_TEST_A_PASS")
            try:
                os.environ["MTRACK_TEST_A_USER"] = "viewer"
                os.environ["MTRACK_TEST_A_PASS"] = "secret"
                cameras = load_hikvision_config(path)
            finally:
                if old_user is None:
                    os.environ.pop("MTRACK_TEST_A_USER", None)
                else:
                    os.environ["MTRACK_TEST_A_USER"] = old_user
                if old_pass is None:
                    os.environ.pop("MTRACK_TEST_A_PASS", None)
                else:
                    os.environ["MTRACK_TEST_A_PASS"] = old_pass

        self.assertEqual(cameras[0].camera.source.source_id, "cam-a")
        self.assertEqual(cameras[0].credentials.username, "viewer")
        self.assertFalse(cameras[0].camera.source.privacy.persist_frames)


if __name__ == "__main__":
    unittest.main()

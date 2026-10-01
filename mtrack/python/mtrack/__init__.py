from .model import Vec3, Observation3D, CalibrationPoint, Residual
from .fusion import fuse_observations
from .lightmap import LightMap
from .feedback import residual
from .sources import ObservationSource, PrivacyPolicy, SourceKind
from .hikvision import HikvisionCamera
from .camera_model import (
    CameraCalibration,
    CameraIntrinsics,
    CameraPose,
    Pixel,
    WorldRay,
    intersect_z_plane,
    pixel_to_world_ray,
    world_to_pixel,
)
from .coverage import CoveragePolygon
from .temporal import AlphaBetaTracker, TrackEstimate
from .authority import AttributeLease, Authority, resolve_attribute
from .evidence import PassiveCalibrationBuffer, PassiveCalibrationSample
from .quality import ConfidenceInputs, effective_confidence
from .calibration_state import CalibrationRecord, CalibrationState
from .sync import SyncWindow, synchronize_observations

__all__ = [
    "Vec3",
    "Observation3D",
    "CalibrationPoint",
    "Residual",
    "fuse_observations",
    "LightMap",
    "residual",
    "ObservationSource",
    "PrivacyPolicy",
    "SourceKind",
    "HikvisionCamera",
    "CameraCalibration",
    "CameraIntrinsics",
    "CameraPose",
    "Pixel",
    "WorldRay",
    "intersect_z_plane",
    "pixel_to_world_ray",
    "world_to_pixel",
    "CoveragePolygon",
    "AlphaBetaTracker",
    "TrackEstimate",
    "AttributeLease",
    "Authority",
    "resolve_attribute",
    "PassiveCalibrationBuffer",
    "PassiveCalibrationSample",
    "ConfidenceInputs",
    "effective_confidence",
    "CalibrationRecord",
    "CalibrationState",
    "SyncWindow",
    "synchronize_observations",
]

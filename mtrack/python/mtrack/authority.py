from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Authority(str, Enum):
    PASSTHROUGH = "passthrough"
    MTRACK_OVERRIDE = "mtrack_override"
    RELEASE = "release"


@dataclass(frozen=True)
class AttributeLease:
    """Declares which semantic attributes MTRACK is allowed to own."""

    fixture_id: int
    attributes: frozenset[str]
    authority: Authority
    expires_at_s: float | None = None

    def owns(self, attribute: str, now_s: float) -> bool:
        if self.authority != Authority.MTRACK_OVERRIDE:
            return False
        if self.expires_at_s is not None and now_s >= self.expires_at_s:
            return False
        return attribute in self.attributes


def resolve_attribute(
    original_value: int,
    mtrack_value: int | None,
    lease: AttributeLease,
    attribute: str,
    now_s: float,
) -> int:
    """Preserve the desk value unless MTRACK explicitly owns the attribute."""
    if mtrack_value is None or not lease.owns(attribute, now_s):
        return original_value
    return mtrack_value

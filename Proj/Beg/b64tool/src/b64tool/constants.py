"""
b64tool constants
Author: Aayush Pandey
"""

from enum import StrEnum
from typing import Final


# ============================================================
# Encoding Formats
# ============================================================

class EncodingFormat(StrEnum):
    BASE64 = "base64"
    BASE64URL = "base64url"
    BASE32 = "base32"
    HEX = "hex"
    URL = "url"


# ============================================================
# Exit Codes
# ============================================================

class ExitCode:
    SUCCESS: Final[int] = 0
    ERROR: Final[int] = 1
    INVALID_INPUT: Final[int] = 2


# ============================================================
# Detection & Peeling Configuration
# ============================================================

PEEL_MAX_DEPTH: Final[int] = 25  # slightly higher than default template
MIN_INPUT_LENGTH: Final[int] = 4
CONFIDENCE_THRESHOLD: Final[float] = 0.60
PRINTABLE_RATIO_THRESHOLD: Final[float] = 0.80

# Terminal display
PREVIEW_LENGTH: Final[int] = 72


# ============================================================
# Detection Score Weights
# Tuned to reduce Base64/Hex ambiguity
# ============================================================

class ScoreWeight:
    # Common bonuses
    DECODE_SUCCESS: Final[float] = 0.15
    PRINTABLE_RESULT: Final[float] = 0.15
    LONGER_INPUT: Final[float] = 0.05

    # Base64
    B64_BASE: Final[float] = 0.40
    B64_VALID_PADDING: Final[float] = 0.10
    B64_SPECIAL_CHARS: Final[float] = 0.10
    B64_MIXED_CASE: Final[float] = 0.10
    B64_NO_SIGNAL_PENALTY: Final[float] = 0.20

    # Base64URL
    B64URL_BASE: Final[float] = 0.30
    B64URL_SAFE_CHARS: Final[float] = 0.25

    # Base32
    B32_BASE: Final[float] = 0.35
    B32_VALID_PADDING: Final[float] = 0.10
    B32_UPPERCASE: Final[float] = 0.10

    # Hex
    HEX_BASE: Final[float] = 0.30
    HEX_SEPARATOR_PRESENT: Final[float] = 0.20
    HEX_ALPHA_CHARS: Final[float] = 0.10
    HEX_NO_ALPHA_PENALTY: Final[float] = 0.15
    HEX_CONSISTENT_CASE: Final[float] = 0.10
    HEX_DECODE_SUCCESS: Final[float] = 0.10

    # URL
    URL_BASE: Final[float] = 0.30
    URL_RATIO_MULTIPLIER: Final[float] = 0.40
    URL_RATIO_CAP: Final[float] = 0.35
    URL_DECODE_CHANGED: Final[float] = 0.15


# ============================================================
# Character Sets (Optimized for O(1) membership testing)
# ============================================================

BASE64_CHARSET: Final[frozenset[str]] = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
)

BASE64URL_CHARSET: Final[frozenset[str]] = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_="
)

BASE32_CHARSET: Final[frozenset[str]] = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567="
)

HEX_CHARSET: Final[frozenset[str]] = frozenset(
    "0123456789abcdefABCDEF"
)

HEX_SEPARATORS: Final[frozenset[str]] = frozenset(
    " :.-"
)
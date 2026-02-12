"""
b64tool detector
Author: Aayush Pandey

Confidence-based encoding detection.
Returns ranked candidate formats with decoded previews (bytes).

Design goals:
- Fast rejection for non-matching formats
- Confidence scoring (0.0–1.0), not binary yes/no
- Strict decode validation via try_decode()
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass

from b64tool.constants import (
    BASE32_CHARSET,
    BASE64_CHARSET,
    BASE64URL_CHARSET,
    CONFIDENCE_THRESHOLD,
    HEX_CHARSET,
    HEX_SEPARATORS,
    MIN_INPUT_LENGTH,
    PRINTABLE_RATIO_THRESHOLD,
    EncodingFormat,
    ScoreWeight as W,
)
from b64tool.encoders import try_decode
from b64tool.utils import is_printable_text


@dataclass(frozen=True, slots=True)
class DetectionResult:
    format: EncodingFormat
    confidence: float
    decoded: bytes | None


# ============================================================
# Scorers
# ============================================================

def _score_base64(data: str) -> float:
    stripped = "".join(data.split())
    if len(stripped) < MIN_INPUT_LENGTH:
        return 0.0
    if not all(c in BASE64_CHARSET for c in stripped):
        return 0.0
    if len(stripped) % 4 != 0:
        return 0.0

    score = W.B64_BASE
    content = stripped.rstrip("=")

    padding = len(stripped) - len(content)
    if padding <= 2:
        score += W.B64_VALID_PADDING

    # Strong signal for standard base64
    if any(c in stripped for c in "+/"):
        score += W.B64_SPECIAL_CHARS

    has_upper = any(c.isupper() for c in content)
    has_lower = any(c.islower() for c in content)

    if has_upper and has_lower:
        score += W.B64_MIXED_CASE
    else:
        # Important disambiguation vs hex-only strings
        if not any(c in stripped for c in "+/=") and not has_upper:
            score -= W.B64_NO_SIGNAL_PENALTY

    if len(stripped) >= 8:
        score += W.LONGER_INPUT

    decoded = try_decode(stripped, EncodingFormat.BASE64)
    if decoded is None:
        return 0.0

    score += W.DECODE_SUCCESS
    if is_printable_text(decoded, threshold=PRINTABLE_RATIO_THRESHOLD):
        score += W.PRINTABLE_RESULT

    return min(max(score, 0.0), 1.0)


def _score_base64url(data: str) -> float:
    stripped = "".join(data.split())
    if len(stripped) < MIN_INPUT_LENGTH:
        return 0.0
    if not all(c in BASE64URL_CHARSET for c in stripped):
        return 0.0

    score = W.B64URL_BASE

    has_url_chars = any(c in stripped for c in "-_")
    has_std_chars = any(c in stripped for c in "+/")

    # If it contains standard chars, it’s probably not base64url
    if has_url_chars and not has_std_chars:
        score += W.B64URL_SAFE_CHARS
    elif not has_url_chars:
        return 0.0

    decoded = try_decode(stripped, EncodingFormat.BASE64URL)
    if decoded is None:
        return 0.0

    score += W.DECODE_SUCCESS
    if is_printable_text(decoded, threshold=PRINTABLE_RATIO_THRESHOLD):
        score += W.PRINTABLE_RESULT

    return min(max(score, 0.0), 1.0)


def _score_base32(data: str) -> float:
    stripped = "".join(data.split()).upper()
    if len(stripped) < MIN_INPUT_LENGTH:
        return 0.0
    if not all(c in BASE32_CHARSET for c in stripped):
        return 0.0
    if len(stripped) % 8 != 0:
        return 0.0

    score = W.B32_BASE

    valid_pad_counts = frozenset({0, 1, 3, 4, 6})
    padding = len(stripped) - len(stripped.rstrip("="))
    if padding in valid_pad_counts:
        score += W.B32_VALID_PADDING

    # If the user pasted uppercase (common), small bonus
    if data == data.upper():
        score += W.B32_UPPERCASE

    decoded = try_decode(stripped, EncodingFormat.BASE32)
    if decoded is None:
        return 0.0

    score += W.DECODE_SUCCESS
    if is_printable_text(decoded, threshold=PRINTABLE_RATIO_THRESHOLD):
        score += W.PRINTABLE_RESULT

    return min(max(score, 0.0), 1.0)


def _score_hex(data: str) -> float:
    stripped = data.strip()
    if len(stripped) < MIN_INPUT_LENGTH:
        return 0.0

    hex_only = stripped
    for sep in HEX_SEPARATORS:
        hex_only = hex_only.replace(sep, "")

    if not hex_only:
        return 0.0
    if not all(c in HEX_CHARSET for c in hex_only):
        return 0.0
    if len(hex_only) % 2 != 0:
        return 0.0

    score = W.HEX_BASE

    if any(sep in stripped for sep in HEX_SEPARATORS):
        score += W.HEX_SEPARATOR_PRESENT

    has_alpha = any(c in "abcdefABCDEF" for c in hex_only)
    if has_alpha:
        score += W.HEX_ALPHA_CHARS
    else:
        score -= W.HEX_NO_ALPHA_PENALTY

    if hex_only == hex_only.lower() or hex_only == hex_only.upper():
        score += W.HEX_CONSISTENT_CASE

    if len(hex_only) >= 8:
        score += W.LONGER_INPUT

    decoded = try_decode(stripped, EncodingFormat.HEX)
    if decoded is None:
        return 0.0

    score += W.HEX_DECODE_SUCCESS
    if is_printable_text(decoded, threshold=PRINTABLE_RATIO_THRESHOLD):
        score += W.PRINTABLE_RESULT

    return min(max(score, 0.0), 1.0)


_URL_PATTERN = re.compile(r"%[0-9a-fA-F]{2}")


def _score_url(data: str) -> float:
    if len(data) < MIN_INPUT_LENGTH:
        return 0.0

    matches = _URL_PATTERN.findall(data)
    if not matches:
        return 0.0

    encoded_char_count = len(matches) * 3
    ratio = encoded_char_count / len(data)
    score = W.URL_BASE + min(ratio * W.URL_RATIO_MULTIPLIER, W.URL_RATIO_CAP)

    decoded = try_decode(data, EncodingFormat.URL)
    if decoded is not None:
        decoded_text = decoded.decode("utf-8", errors="replace")
        if decoded_text != data:
            score += W.URL_DECODE_CHANGED

    return min(max(score, 0.0), 1.0)


_SCORERS: dict[EncodingFormat, Callable[[str], float]] = {
    EncodingFormat.BASE64: _score_base64,
    EncodingFormat.BASE64URL: _score_base64url,
    EncodingFormat.BASE32: _score_base32,
    EncodingFormat.HEX: _score_hex,
    EncodingFormat.URL: _score_url,
}


# ============================================================
# Public API
# ============================================================

def score_all_formats(data: str) -> dict[EncodingFormat, float]:
    return {fmt: scorer(data) for fmt, scorer in _SCORERS.items()}


def detect_encoding(data: str) -> list[DetectionResult]:
    results: list[DetectionResult] = []

    for fmt, confidence in score_all_formats(data).items():
        if confidence >= CONFIDENCE_THRESHOLD:
            decoded = try_decode(data, fmt)
            results.append(
                DetectionResult(
                    format=fmt,
                    confidence=round(confidence, 2),
                    decoded=decoded,
                )
            )

    results.sort(key=lambda r: r.confidence, reverse=True)
    return results


def detect_best(data: str) -> DetectionResult | None:
    results = detect_encoding(data)
    return results[0] if results else None
"""
b64tool peeler
Author: Aayush Pandey

Recursive layer peeling (iterative loop) to strip stacked encodings.

Key behavior:
- Uses detect_best() each round
- Stops when confidence drops below threshold, decode fails, max depth hit,
  or decoded bytes are not valid UTF-8 (likely reached binary/original payload)
"""

from __future__ import annotations

from dataclasses import dataclass

from b64tool.constants import (
    CONFIDENCE_THRESHOLD,
    PEEL_MAX_DEPTH,
    PREVIEW_LENGTH,
    EncodingFormat,
)
from b64tool.detector import DetectionResult, detect_best, score_all_formats
from b64tool.encoders import try_decode
from b64tool.utils import safe_bytes_preview, truncate


@dataclass(frozen=True, slots=True)
class PeelLayer:
    depth: int
    format: EncodingFormat
    confidence: float
    input_preview: str
    output_preview: str
    # Optional: keep verbose per-format scores for this layer
    scores: dict[EncodingFormat, float] | None = None


@dataclass(frozen=True, slots=True)
class PeelResult:
    layers: tuple[PeelLayer, ...]
    final_output: bytes
    success: bool


def peel(
    data: str,
    *,
    max_depth: int = PEEL_MAX_DEPTH,
    verbose: bool = False,
) -> PeelResult:
    """
    Peel stacked encodings from `data` until a stop condition is hit.

    Returns:
      PeelResult with ordered layers and final_output bytes.
    """
    current_text = data.strip()
    current_bytes: bytes | None = None
    layers: list[PeelLayer] = []

    for depth in range(1, max_depth + 1):
        det: DetectionResult | None = detect_best(current_text)
        if det is None:
            break
        if det.confidence < CONFIDENCE_THRESHOLD:
            break

        decoded = det.decoded
        if decoded is None:
            # (Shouldn't happen if detector used try_decode, but keep safe)
            decoded = try_decode(current_text, det.format)
        if decoded is None:
            break

        input_preview = truncate(current_text, PREVIEW_LENGTH)
        output_preview = safe_bytes_preview(decoded, PREVIEW_LENGTH)

        scores = score_all_formats(current_text) if verbose else None

        layers.append(
            PeelLayer(
                depth=depth,
                format=det.format,
                confidence=det.confidence,
                input_preview=input_preview,
                output_preview=output_preview,
                scores=scores,
            )
        )

        current_bytes = decoded

        # If the decoded output isn't UTF-8 text, we likely reached the "real" blob.
        try:
            current_text = decoded.decode("utf-8").strip()
        except UnicodeDecodeError:
            break

        # If it decodes to empty, stop (nothing more to peel)
        if not current_text:
            break

    if current_bytes is None:
        # No layers peeled: final output is original bytes (best-effort)
        final = current_text.encode("utf-8", errors="replace")
        return PeelResult(layers=tuple(), final_output=final, success=False)

    return PeelResult(layers=tuple(layers), final_output=current_bytes, success=len(layers) > 0)
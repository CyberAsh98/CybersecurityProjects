"""
b64tool utils
Author: Aayush Pandey

Input resolution + safe preview helpers.
Designed to be pipeline-friendly (stdin/stdout) and robust for security workflows.
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from b64tool.constants import PREVIEW_LENGTH, PRINTABLE_RATIO_THRESHOLD


# ============================================================
# Input Resolution
# Priority: --file > positional arg > stdin pipe
# ============================================================

def resolve_input_bytes(data: str | None, file: Path | None) -> bytes:
    """
    Resolve input into raw bytes.
    - If file provided: read bytes from file
    - Else if data provided: encode to UTF-8 bytes
    - Else if stdin piped: read stdin bytes
    - Else: error
    """
    if file is not None:
        if not file.exists():
            raise typer.BadParameter(f"File not found: {file}")
        if not file.is_file():
            raise typer.BadParameter(f"Not a file: {file}")
        return file.read_bytes()

    if data is not None:
        return data.encode("utf-8")

    if not sys.stdin.isatty():
        return sys.stdin.buffer.read()

    raise typer.BadParameter(
        "No input provided. Pass an argument, use --file, or pipe stdin."
    )


def resolve_input_text(data: str | None, file: Path | None) -> str:
    """
    Resolve input into text (string).
    - If file provided: read text (utf-8) and strip
    - Else if data provided: strip
    - Else if stdin piped: read stdin text and strip
    - Else: error
    """
    if file is not None:
        if not file.exists():
            raise typer.BadParameter(f"File not found: {file}")
        if not file.is_file():
            raise typer.BadParameter(f"Not a file: {file}")
        return file.read_text("utf-8", errors="replace").strip()

    if data is not None:
        return data.strip()

    if not sys.stdin.isatty():
        return sys.stdin.read().strip()

    raise typer.BadParameter(
        "No input provided. Pass an argument, use --file, or pipe stdin."
    )


# ============================================================
# Output / Preview Helpers
# ============================================================

def is_piped_stdout() -> bool:
    """
    True if stdout is piped (not a TTY).
    In piped mode, we should avoid rich formatting on stdout.
    """
    return not sys.stdout.isatty()


def truncate(text: str, length: int = PREVIEW_LENGTH) -> str:
    if len(text) <= length:
        return text
    return text[:length] + "..."


def safe_bytes_preview(data: bytes, length: int = PREVIEW_LENGTH) -> str:
    """
    Try to decode bytes to UTF-8 for preview; fallback to hex.
    Never throws.
    """
    if not data:
        return ""
    try:
        text = data.decode("utf-8")
        return truncate(text, length)
    except (UnicodeDecodeError, ValueError):
        return truncate(data.hex(), length)


def is_printable_text(data: bytes, threshold: float = PRINTABLE_RATIO_THRESHOLD) -> bool:
    """
    Heuristic: decoded bytes look like human-readable text.
    Used to boost detection confidence.
    """
    if not data:
        return False
    try:
        text = data.decode("utf-8")
    except (UnicodeDecodeError, ValueError):
        return False

    printable = sum(1 for c in text if c.isprintable() or c in "\n\r\t")
    return (printable / max(len(text), 1)) >= threshold
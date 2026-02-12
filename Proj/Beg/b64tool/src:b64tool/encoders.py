"""
b64tool encoders
Author: Aayush Pandey

Pure encoding / decoding functions.
No CLI logic. No printing. No side effects.

Registry-based dispatch (Open-Closed Principle).
"""

from __future__ import annotations

import base64 as b64
import binascii
from collections.abc import Callable
from urllib.parse import quote, quote_plus, unquote, unquote_plus

from b64tool.constants import EncodingFormat


# ============================================================
# Type Aliases (PEP 695)
# ============================================================

type EncoderFn = Callable[[bytes], str]
type DecoderFn = Callable[[str], bytes]


# ============================================================
# Base64
# ============================================================

def encode_base64(data: bytes) -> str:
    return b64.b64encode(data).decode("ascii")


def decode_base64(data: str) -> bytes:
    cleaned = "".join(data.split())
    # validate=True enforces strict RFC 4648 compliance
    return b64.b64decode(cleaned, validate=True)


# ============================================================
# Base64URL (JWT-safe variant)
# ============================================================

def encode_base64url(data: bytes) -> str:
    return b64.urlsafe_b64encode(data).decode("ascii")


def decode_base64url(data: str) -> bytes:
    cleaned = "".join(data.split())
    return b64.urlsafe_b64decode(cleaned)


# ============================================================
# Base32
# ============================================================

def encode_base32(data: bytes) -> str:
    return b64.b32encode(data).decode("ascii")


def decode_base32(data: str) -> bytes:
    cleaned = "".join(data.split()).upper()
    return b64.b32decode(cleaned)


# ============================================================
# Hex
# ============================================================

def encode_hex(data: bytes) -> str:
    return data.hex()


def decode_hex(data: str) -> bytes:
    cleaned = data.strip()
    for sep in (" ", ":", "-", "."):
        cleaned = cleaned.replace(sep, "")
    return bytes.fromhex(cleaned)


# ============================================================
# URL Encoding
# ============================================================

def encode_url(data: bytes, *, form: bool = False) -> str:
    text = data.decode("utf-8")
    if form:
        return quote_plus(text)
    return quote(text, safe="")


def decode_url(data: str, *, form: bool = False) -> bytes:
    if form:
        return unquote_plus(data).encode("utf-8")
    return unquote(data).encode("utf-8")


# ============================================================
# Registry (Dispatch Pattern)
# ============================================================

ENCODER_REGISTRY: dict[
    EncodingFormat,
    tuple[EncoderFn, DecoderFn],
] = {
    EncodingFormat.BASE64: (encode_base64, decode_base64),
    EncodingFormat.BASE64URL: (encode_base64url, decode_base64url),
    EncodingFormat.BASE32: (encode_base32, decode_base32),
    EncodingFormat.HEX: (encode_hex, decode_hex),
    EncodingFormat.URL: (
        lambda data: encode_url(data),
        lambda data: decode_url(data),
    ),
}


def encode(data: bytes, fmt: EncodingFormat) -> str:
    encoder_fn, _ = ENCODER_REGISTRY[fmt]
    return encoder_fn(data)


def decode(data: str, fmt: EncodingFormat) -> bytes:
    _, decoder_fn = ENCODER_REGISTRY[fmt]
    return decoder_fn(data)


def try_decode(data: str, fmt: EncodingFormat) -> bytes | None:
    """
    Safe decode wrapper for detection logic.
    Returns None instead of raising.
    """
    try:
        return decode(data, fmt)
    except (
        ValueError,
        binascii.Error,
        UnicodeDecodeError,
        UnicodeEncodeError,
    ):
        return None
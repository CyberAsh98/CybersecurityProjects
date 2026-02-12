# tests/test_encoders.py

import pytest

from b64tool.constants import EncodingFormat
from b64tool.encoders import (
    decode,
    decode_base32,
    decode_base64,
    decode_base64url,
    decode_hex,
    decode_url,
    encode,
    encode_base32,
    encode_base64,
    encode_base64url,
    encode_hex,
    encode_url,
    try_decode,
)


class TestBase64:
    def test_encode_decode_roundtrip(self) -> None:
        raw = b"Hello World"
        enc = encode_base64(raw)
        dec = decode_base64(enc)
        assert dec == raw

    def test_decode_strict_rejects_invalid(self) -> None:
        with pytest.raises(Exception):
            decode_base64("!!!invalid!!!")


class TestBase64URL:
    def test_encode_decode_roundtrip(self) -> None:
        raw = b"test-data_value"
        enc = encode_base64url(raw)
        dec = decode_base64url(enc)
        assert dec == raw

    def test_urlsafe_contains_no_plus_slash(self) -> None:
        raw = b"\xff\xee\xdd\xcc\xbb\xaa"
        enc = encode_base64url(raw)
        assert "+" not in enc
        assert "/" not in enc


class TestBase32:
    def test_encode_decode_roundtrip(self) -> None:
        raw = b"Hello World"
        enc = encode_base32(raw)
        dec = decode_base32(enc)
        assert dec == raw

    def test_decode_accepts_lowercase_input(self) -> None:
        raw = b"Hello"
        enc = encode_base32(raw).lower()
        dec = decode_base32(enc)
        assert dec == raw


class TestHex:
    def test_encode_decode_roundtrip(self) -> None:
        raw = b"\x00\x01\xffhello"
        enc = encode_hex(raw)
        dec = decode_hex(enc)
        assert dec == raw

    def test_decode_accepts_separators(self) -> None:
        enc = "48:65:6c:6c:6f"
        dec = decode_hex(enc)
        assert dec == b"Hello"


class TestURL:
    def test_encode_decode_roundtrip(self) -> None:
        raw = "hello world&key=val".encode("utf-8")
        enc = encode_url(raw)
        dec = decode_url(enc)
        assert dec == raw

    def test_form_encoding_roundtrip(self) -> None:
        raw = "hello world".encode("utf-8")
        enc = encode_url(raw, form=True)  # space => +
        assert "+" in enc
        dec = decode_url(enc, form=True)
        assert dec == raw


class TestRegistryDispatch:
    def test_encode_decode_dispatch_all(self) -> None:
        raw = b"secret payload"
        for fmt in (
            EncodingFormat.BASE64,
            EncodingFormat.BASE64URL,
            EncodingFormat.BASE32,
            EncodingFormat.HEX,
        ):
            enc = encode(raw, fmt)
            dec = decode(enc, fmt)
            assert dec == raw

    def test_try_decode_returns_none_on_failure(self) -> None:
        assert try_decode("!!!invalid!!!", EncodingFormat.BASE64) is None
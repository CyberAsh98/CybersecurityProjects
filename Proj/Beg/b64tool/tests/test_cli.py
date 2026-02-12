# tests/test_cli.py

from typer.testing import CliRunner

from b64tool.cli import app

runner = CliRunner()


class TestEncodeCommand:
    def test_encode_base64_default(self) -> None:
        result = runner.invoke(app, ["encode", "Hello World"])
        assert result.exit_code == 0
        assert "SGVsbG8gV29ybGQ=" in result.output

    def test_encode_hex(self) -> None:
        result = runner.invoke(app, ["encode", "Hello", "--format", "hex"])
        assert result.exit_code == 0
        assert "48656c6c6f" in result.output

    def test_encode_base32(self) -> None:
        result = runner.invoke(app, ["encode", "Hello", "--format", "base32"])
        assert result.exit_code == 0
        # "Hello" base32 starts with this
        assert "JBSWY3DP" in result.output

    def test_encode_url(self) -> None:
        result = runner.invoke(app, ["encode", "hello world&test", "--format", "url"])
        assert result.exit_code == 0
        # In URL encoding, space becomes %20 by default
        assert "%20" in result.output

    def test_encode_empty_string(self) -> None:
        result = runner.invoke(app, ["encode", ""])
        assert result.exit_code == 0


class TestDecodeCommand:
    def test_decode_base64_default(self) -> None:
        result = runner.invoke(app, ["decode", "SGVsbG8gV29ybGQ="])
        assert result.exit_code == 0
        assert "Hello World" in result.output

    def test_decode_hex(self) -> None:
        result = runner.invoke(app, ["decode", "48656c6c6f", "--format", "hex"])
        assert result.exit_code == 0
        assert "Hello" in result.output

    def test_decode_invalid_base64_fails(self) -> None:
        result = runner.invoke(app, ["decode", "!!!invalid!!!"])
        assert result.exit_code != 0


class TestDetectCommand:
    def test_detect_base64_outputs_format_in_piped_mode(self) -> None:
        # In tests, stdout is not a TTY => piped mode => detect prints best format only
        result = runner.invoke(app, ["detect", "SGVsbG8gV29ybGQ="])
        assert result.exit_code == 0
        assert result.output.strip().lower() in {"base64", "base64url"}

    def test_detect_hex_outputs_format(self) -> None:
        result = runner.invoke(app, ["detect", "48656c6c6f20576f726c64"])
        assert result.exit_code == 0
        assert result.output.strip().lower() == "hex"

    def test_detect_no_match_outputs_nothing(self) -> None:
        result = runner.invoke(app, ["detect", "just plain text"])
        assert result.exit_code == 0
        # piped-mode detect prints nothing when no confident match
        assert result.output.strip() == ""


class TestPeelCommand:
    def test_peel_single_layer_outputs_final_payload_in_piped_mode(self) -> None:
        # In piped mode, peel prints final_output only (not Rich layer panels)
        result = runner.invoke(app, ["peel", "SGVsbG8gV29ybGQ="])
        assert result.exit_code == 0
        assert "Hello World" in result.output

    def test_peel_no_encoding_outputs_original_text_bytes(self) -> None:
        result = runner.invoke(app, ["peel", "hello world"])
        assert result.exit_code == 0
        assert "hello world" in result.output


class TestChainCommand:
    def test_chain_single_step_base64(self) -> None:
        result = runner.invoke(app, ["chain", "Hello", "--steps", "base64"])
        assert result.exit_code == 0
        assert "SGVsbG8=" in result.output

    def test_chain_multiple_steps_runs(self) -> None:
        result = runner.invoke(app, ["chain", "Hi", "--steps", "base64,hex"])
        assert result.exit_code == 0
        # final output should be hex text
        out = result.output.strip().lower()
        assert all(c in "0123456789abcdef" for c in out)
        assert len(out) > 0

    def test_chain_invalid_format_fails(self) -> None:
        result = runner.invoke(app, ["chain", "test", "--steps", "fake"])
        assert result.exit_code != 0


class TestVersionFlag:
    def test_version_output(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "b64tool" in result.output.lower()
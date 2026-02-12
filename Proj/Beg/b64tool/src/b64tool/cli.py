"""
b64tool CLI
Author: Aayush Pandey

Typer-based CLI:
- encode / decode
- detect (confidence scoring)
- peel (multi-layer decoding)
- chain (multi-step encoding)
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from b64tool import __version__
from b64tool.constants import EncodingFormat, ExitCode, PEEL_MAX_DEPTH
from b64tool.detector import detect_encoding, score_all_formats
from b64tool.encoders import decode, decode_url, encode, encode_url
from b64tool.formatter import (
    print_chain_result,
    print_decoded,
    print_detection,
    print_encoded,
    print_peel_result,
)
from b64tool.peeler import peel
from b64tool.utils import resolve_input_bytes, resolve_input_text

app = typer.Typer(
    name="b64tool",
    help="Multi-format encoding/decoding CLI with recursive layer peeling.",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)

_console = Console(stderr=True)


def _version_callback(value: bool) -> None:
    if value:
        _console.print(f"b64tool v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    return


# ---------------------------------------------------------------------
# encode
# ---------------------------------------------------------------------


@app.command(name="encode")
def encode_cmd(
    data: Annotated[str | None, typer.Argument(help="Data to encode.")] = None,
    fmt: Annotated[
        EncodingFormat,
        typer.Option("--format", "-f", help="Target encoding format."),
    ] = EncodingFormat.BASE64,
    file: Annotated[
        Path | None,
        typer.Option("--file", "-i", help="Read input from file."),
    ] = None,
    form: Annotated[
        bool,
        typer.Option("--form", help="Form-encoding for URL (space becomes +)."),
    ] = False,
) -> None:
    try:
        raw = resolve_input_bytes(data, file)
        if fmt == EncodingFormat.URL:
            result = encode_url(raw, form=form)
        else:
            result = encode(raw, fmt)
        print_encoded(result, fmt)
    except typer.BadParameter:
        raise
    except Exception as exc:
        _console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=ExitCode.ERROR) from None


# ---------------------------------------------------------------------
# decode
# ---------------------------------------------------------------------


@app.command(name="decode")
def decode_cmd(
    data: Annotated[str | None, typer.Argument(help="Data to decode.")] = None,
    fmt: Annotated[
        EncodingFormat,
        typer.Option("--format", "-f", help="Source encoding format."),
    ] = EncodingFormat.BASE64,
    file: Annotated[
        Path | None,
        typer.Option("--file", "-i", help="Read input from file."),
    ] = None,
    form: Annotated[
        bool,
        typer.Option("--form", help="Form-decoding for URL (+ becomes space)."),
    ] = False,
) -> None:
    try:
        text = resolve_input_text(data, file)
        if fmt == EncodingFormat.URL:
            result = decode_url(text, form=form)
        else:
            result = decode(text, fmt)
        print_decoded(result)
    except typer.BadParameter:
        raise
    except Exception as exc:
        _console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=ExitCode.ERROR) from None


# ---------------------------------------------------------------------
# detect
# ---------------------------------------------------------------------


@app.command(name="detect")
def detect_cmd(
    data: Annotated[str | None, typer.Argument(help="Data to analyze.")] = None,
    file: Annotated[
        Path | None,
        typer.Option("--file", "-i", help="Read input from file."),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-V", help="Show per-format score breakdown."),
    ] = False,
) -> None:
    try:
        text = resolve_input_text(data, file)
        results = detect_encoding(text)
        scores = score_all_formats(text) if verbose else None
        print_detection(results, verbose_scores=scores)
    except typer.BadParameter:
        raise
    except Exception as exc:
        _console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=ExitCode.ERROR) from None


# ---------------------------------------------------------------------
# peel
# ---------------------------------------------------------------------


@app.command(name="peel")
def peel_cmd(
    data: Annotated[
        str | None,
        typer.Argument(help="Data to recursively decode."),
    ] = None,
    file: Annotated[
        Path | None,
        typer.Option("--file", "-i", help="Read input from file."),
    ] = None,
    max_depth: Annotated[
        int,
        typer.Option("--max-depth", "-d", help="Maximum decoding layers."),
    ] = PEEL_MAX_DEPTH,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-V", help="Show score breakdown at each layer."),
    ] = False,
) -> None:
    try:
        text = resolve_input_text(data, file)
        result = peel(text, max_depth=max_depth, verbose=verbose)
        print_peel_result(result, verbose=verbose)
    except typer.BadParameter:
        raise
    except Exception as exc:
        _console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=ExitCode.ERROR) from None


# ---------------------------------------------------------------------
# chain
# ---------------------------------------------------------------------


@app.command(name="chain")
def chain_cmd(
    data: Annotated[
        str | None,
        typer.Argument(help="Data to encode through chain."),
    ] = None,
    steps: Annotated[
        str,
        typer.Option(
            "--steps",
            "-s",
            help="Comma-separated encoding formats (e.g. base64,hex,url).",
        ),
    ] = "base64",
    file: Annotated[
        Path | None,
        typer.Option("--file", "-i", help="Read input from file."),
    ] = None,
) -> None:
    try:
        raw = resolve_input_bytes(data, file)
        formats = _parse_chain_steps(steps)

        intermediates: list[tuple[EncodingFormat, str]] = []
        current = raw

        for step_fmt in formats:
            encoded = encode(current, step_fmt) if step_fmt != EncodingFormat.URL else encode_url(current)
            intermediates.append((step_fmt, encoded))
            current = encoded.encode("utf-8")

        final = intermediates[-1][1] if intermediates else ""
        print_chain_result(intermediates, final)
    except typer.BadParameter:
        raise
    except Exception as exc:
        _console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=ExitCode.ERROR) from None


def _parse_chain_steps(raw: str) -> list[EncodingFormat]:
    formats: list[EncodingFormat] = []
    valid_names = ", ".join(f.value for f in EncodingFormat)

    for step in raw.split(","):
        cleaned = step.strip().lower()
        try:
            formats.append(EncodingFormat(cleaned))
        except ValueError:
            raise typer.BadParameter(
                f"Unknown format '{cleaned}'. Valid formats: {valid_names}"
            ) from None

    if not formats:
        raise typer.BadParameter("At least one step is required.")

    return formats
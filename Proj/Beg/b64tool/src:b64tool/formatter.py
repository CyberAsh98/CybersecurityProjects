"""
b64tool formatter
Author: Aayush Pandey

Handles all terminal rendering.
- Rich panels/tables when interactive
- Raw stdout when piped (pipeline-safe)
- All Rich output goes to stderr
"""

from __future__ import annotations

import sys
from typing import Iterable

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from b64tool.constants import PREVIEW_LENGTH, EncodingFormat
from b64tool.detector import DetectionResult
from b64tool.peeler import PeelLayer, PeelResult
from b64tool.utils import safe_bytes_preview, truncate


# Rich output goes to stderr so stdout stays clean for piping
console = Console(stderr=True)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def is_piped() -> bool:
    return not sys.stdout.isatty()


def _confidence_color(conf: float) -> str:
    if conf >= 0.9:
        return "green"
    if conf >= 0.7:
        return "yellow"
    return "red"


def _confidence_percent(conf: float) -> str:
    return f"{round(conf * 100)}%"


# ---------------------------------------------------------------------
# Encode / Decode
# ---------------------------------------------------------------------


def print_encoded(result: str, fmt: EncodingFormat) -> None:
    if is_piped():
        print(result)
        return

    console.print(
        Panel(
            result,
            title=f"[bold cyan]Encoded ({fmt.value})[/bold cyan]",
            expand=False,
        )
    )


def print_decoded(result: bytes) -> None:
    if is_piped():
        # Raw bytes to stdout
        try:
            sys.stdout.buffer.write(result)
        except Exception:
            print(result.decode("utf-8", errors="replace"))
        return

    preview = safe_bytes_preview(result, PREVIEW_LENGTH)

    console.print(
        Panel(
            preview,
            title="[bold green]Decoded Output[/bold green]",
            expand=False,
        )
    )


# ---------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------


def print_detection(
    results: Iterable[DetectionResult],
    *,
    verbose_scores: dict[EncodingFormat, float] | None = None,
) -> None:
    results = list(results)

    if is_piped():
        if not results:
            return
        # Print best match only in piped mode
        best = results[0]
        print(best.format.value)
        return

    if not results:
        console.print("[red]No encoding confidently detected.[/red]")
        return

    table = Table(title="Encoding Detection", show_lines=True)
    table.add_column("Format", style="cyan", no_wrap=True)
    table.add_column("Confidence", style="magenta")
    table.add_column("Decoded Preview", style="white")

    for r in results:
        preview = (
            safe_bytes_preview(r.decoded, PREVIEW_LENGTH)
            if r.decoded
            else "-"
        )
        color = _confidence_color(r.confidence)
        table.add_row(
            r.format.value,
            f"[{color}]{_confidence_percent(r.confidence)}[/{color}]",
            truncate(preview, PREVIEW_LENGTH),
        )

    console.print(table)

    if verbose_scores:
        console.print("\n[bold]Score Breakdown:[/bold]")
        breakdown = Table(show_header=True)
        breakdown.add_column("Format")
        breakdown.add_column("Score")

        for fmt, score in verbose_scores.items():
            breakdown.add_row(fmt.value, f"{round(score, 3)}")

        console.print(breakdown)


# ---------------------------------------------------------------------
# Peel
# ---------------------------------------------------------------------


def print_peel_result(result: PeelResult, *, verbose: bool = False) -> None:
    if is_piped():
        # Only final output to stdout
        try:
            sys.stdout.buffer.write(result.final_output)
        except Exception:
            print(result.final_output.decode("utf-8", errors="replace"))
        return

    if not result.layers:
        console.print("[yellow]No encodings peeled.[/yellow]")
        return

    for layer in result.layers:
        color = _confidence_color(layer.confidence)

        console.print(
            Panel(
                f"[bold]Input:[/bold]  {layer.input_preview}\n"
                f"[bold]Output:[/bold] {layer.output_preview}",
                title=(
                    f"Layer {layer.depth} — "
                    f"[{color}]{layer.format.value} "
                    f"({_confidence_percent(layer.confidence)})[/{color}]"
                ),
                expand=False,
            )
        )

        if verbose and layer.scores:
            score_table = Table(title="Score Breakdown", show_lines=False)
            score_table.add_column("Format")
            score_table.add_column("Score")
            for fmt, score in layer.scores.items():
                score_table.add_row(fmt.value, f"{round(score, 3)}")
            console.print(score_table)

    final_preview = safe_bytes_preview(result.final_output, PREVIEW_LENGTH)

    console.print(
        Panel(
            final_preview,
            title="[bold green]Final Output[/bold green]",
            expand=False,
        )
    )


# ---------------------------------------------------------------------
# Chain
# ---------------------------------------------------------------------


def print_chain_result(
    intermediates: list[tuple[EncodingFormat, str]],
    final: str,
) -> None:
    if is_piped():
        print(final)
        return

    table = Table(title="Encoding Chain", show_lines=True)
    table.add_column("Step", style="cyan")
    table.add_column("Format", style="magenta")
    table.add_column("Output Preview", style="white")

    for idx, (fmt, value) in enumerate(intermediates, start=1):
        table.add_row(
            str(idx),
            fmt.value,
            truncate(value, PREVIEW_LENGTH),
        )

    console.print(table)

    console.print(
        Panel(
            truncate(final, PREVIEW_LENGTH),
            title="[bold cyan]Final Encoded Output[/bold cyan]",
            expand=False,
        )
    )
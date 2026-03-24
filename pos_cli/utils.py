"""Shared utilities for formatting and display."""

from rich.console import Console
from rich.table import Table

console = Console()
err_console = Console(stderr=True)


def print_table(title: str, columns: list[tuple[str, str]], rows: list[list[str]]):
    """Print a rich table with the given columns and rows.

    columns: list of (header, style) tuples
    rows: list of row data (each row is a list of strings)
    """
    table = Table(title=title, show_lines=False)
    for header, style in columns:
        table.add_column(header, style=style)
    for row in rows:
        table.add_row(*row)
    console.print(table)


def print_dict(title: str, data: dict, styles: dict | None = None):
    """Print a key-value dict as a two-column table."""
    styles = styles or {}
    table = Table(title=title, show_header=False, show_lines=False)
    table.add_column("Key", style="bold cyan", min_width=16)
    table.add_column("Value")
    for k, v in data.items():
        val = str(v) if v is not None else "-"
        style = styles.get(k, "")
        table.add_row(k, f"[{style}]{val}[/{style}]" if style else val)
    console.print(table)


def print_success(msg: str):
    console.print(f"[bold green]✓[/bold green] {msg}")


def print_error(msg: str):
    err_console.print(f"[bold red]✗[/bold red] {msg}")


def print_warning(msg: str):
    err_console.print(f"[bold yellow]![/bold yellow] {msg}")


def parse_json_or_html(resp):
    """Try to parse JSON from a response, handling HTML redirects."""
    try:
        return resp.json()
    except Exception:
        if "login" in resp.url:
            return {"error": "Session expired. Please run: pos login"}
        return {"error": f"Unexpected response (HTTP {resp.status_code})"}

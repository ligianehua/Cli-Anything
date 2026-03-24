"""Cash register session commands."""

import click

from ..client import PosClient
from ..utils import parse_json_or_html, print_dict, print_error, print_success


@click.group()
def register():
    """Cash register session management."""
    pass


@register.command("status")
def register_status():
    """Check current register session status."""
    client = PosClient()
    resp = client.get("/cashier/register/status")
    data = parse_json_or_html(resp)

    if "error" in data:
        print_error(data["error"])
        return

    session = data.get("session", data)
    if not session or session.get("status") == "closed":
        click.echo("Register is CLOSED. Run: pos register open")
        return

    print_dict("Register Session", {
        "Status": "OPEN",
        "Opened At": session.get("opened_at", session.get("created_at", "-")),
        "Opening Balance": f"₱{session.get('opening_balance', 0):.2f}",
        "Cash Sales": f"₱{session.get('cash_sales', 0):.2f}",
        "Expected Cash": f"₱{session.get('expected_cash', 0):.2f}",
    })


@register.command("open")
@click.option("--balance", "-b", required=True, type=float, help="Opening cash balance")
def open_register(balance):
    """Open a new register session."""
    client = PosClient()
    resp = client.post("/cashier/register/open", {"opening_balance": balance})
    if resp.status_code in (200, 201, 302):
        print_success(f"Register opened with ₱{balance:.2f}")
    else:
        data = parse_json_or_html(resp)
        print_error(f"Failed: {data.get('error', data.get('message', resp.status_code))}")


@register.command("close")
@click.option("--cash-count", "-c", required=True, type=float, help="Actual cash counted")
def close_register(cash_count):
    """Close the current register session."""
    client = PosClient()
    resp = client.post("/cashier/register/close", {"closing_balance": cash_count})
    data = parse_json_or_html(resp)

    if resp.status_code in (200, 302):
        variance = data.get("variance", 0)
        expected = data.get("expected", 0)
        print_success(f"Register closed. Expected: ₱{expected:.2f}, Counted: ₱{cash_count:.2f}, Variance: ₱{variance:.2f}")
    else:
        print_error(f"Failed: {data.get('error', data.get('message', resp.status_code))}")


@register.command("reading")
@click.argument("type_", metavar="TYPE", type=click.Choice(["x", "z"]))
def reading(type_):
    """Generate X or Z reading report."""
    client = PosClient()
    resp = client.get(f"/cashier/reading/{type_}")
    data = parse_json_or_html(resp)

    if "error" in data:
        print_error(data["error"])
        return

    reading_data = data.get("reading", data)
    print_dict(f"{'X' if type_ == 'x' else 'Z'} Reading", {
        "Date": reading_data.get("date", "-"),
        "Gross Sales": f"₱{reading_data.get('gross_sales', 0):.2f}",
        "Net Sales": f"₱{reading_data.get('net_sales', 0):.2f}",
        "Returns": f"₱{reading_data.get('returns', 0):.2f}",
        "Cash Sales": f"₱{reading_data.get('cash_sales', 0):.2f}",
        "Digital Sales": f"₱{reading_data.get('digital_sales', 0):.2f}",
        "Credit Sales": f"₱{reading_data.get('credit_sales', 0):.2f}",
        "Transaction Count": reading_data.get("transaction_count", 0),
    })

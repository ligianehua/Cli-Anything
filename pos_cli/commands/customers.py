"""Customer and credit management commands."""

import click

from ..client import PosClient
from ..utils import parse_json_or_html, print_dict, print_error, print_success, print_table


@click.group()
def customers():
    """Customer and credit management."""
    pass


@customers.command("list")
@click.option("--search", "-s", default=None, help="Search by name")
def list_customers(search):
    """List all customers."""
    client = PosClient()
    params = {}
    if search:
        params["search"] = search
    resp = client.get("/admin/customers", params=params)
    data = parse_json_or_html(resp)

    if "error" in data:
        print_error(data["error"])
        return

    items = data if isinstance(data, list) else data.get("data", data.get("customers", []))
    if not items:
        click.echo("No customers found.")
        return

    rows = []
    for c in items:
        rows.append([
            str(c.get("id", "")),
            c.get("name", ""),
            c.get("phone", "-"),
            c.get("email", "-"),
            f"₱{c.get('total_credit', c.get('balance', 0)):.2f}",
        ])

    print_table(
        "Customers",
        [("ID", "cyan"), ("Name", "white"), ("Phone", "dim"), ("Email", "dim"), ("Credit", "red")],
        rows,
    )


@customers.command("create")
@click.option("--name", "-n", required=True, help="Customer name")
@click.option("--phone", "-p", default="", help="Phone number")
@click.option("--email", "-e", default="", help="Email address")
@click.option("--address", "-a", default="", help="Address")
def create_customer(name, phone, email, address):
    """Add a new customer."""
    client = PosClient()
    resp = client.post("/admin/customers", {
        "name": name,
        "phone": phone,
        "email": email,
        "address": address,
    })
    if resp.status_code in (200, 201, 302):
        print_success(f"Customer '{name}' created")
    else:
        data = parse_json_or_html(resp)
        print_error(f"Failed: {data.get('error', data.get('errors', resp.status_code))}")


@customers.command("show")
@click.argument("customer_id", type=int)
def show_customer(customer_id):
    """Show customer details and credit info."""
    client = PosClient()
    resp = client.get(f"/admin/customers/{customer_id}")
    data = parse_json_or_html(resp)

    if "error" in data:
        print_error(data["error"])
        return

    c = data.get("customer", data)
    print_dict("Customer", {
        "ID": c.get("id"),
        "Name": c.get("name"),
        "Phone": c.get("phone", "-"),
        "Email": c.get("email", "-"),
        "Address": c.get("address", "-"),
        "Total Credit": f"₱{c.get('total_credit', 0):.2f}",
        "Loyalty Points": c.get("loyalty_points", 0),
    })


# --- Credit sub-commands ---

@click.group()
def credits():
    """Customer credit and debt management."""
    pass


@credits.command("list")
@click.option("--status", type=click.Choice(["pending", "paid", "overdue"]), help="Filter by status")
def list_credits(status):
    """List all outstanding credits."""
    client = PosClient()
    params = {}
    if status:
        params["status"] = status
    resp = client.get("/admin/credits", params=params)
    data = parse_json_or_html(resp)

    if "error" in data:
        print_error(data["error"])
        return

    items = data if isinstance(data, list) else data.get("data", data.get("credits", []))
    if not items:
        click.echo("No credits found.")
        return

    rows = []
    for cr in items:
        customer = cr.get("customer", {}) if isinstance(cr.get("customer"), dict) else {}
        rows.append([
            str(cr.get("id", "")),
            customer.get("name", str(cr.get("customer_id", ""))),
            f"₱{cr.get('amount', 0):.2f}",
            f"₱{cr.get('paid', 0):.2f}",
            f"₱{cr.get('balance', cr.get('amount', 0) - cr.get('paid', 0)):.2f}",
            cr.get("due_date", "-"),
        ])

    print_table(
        "Credits",
        [("ID", "cyan"), ("Customer", "white"), ("Amount", "red"), ("Paid", "green"), ("Balance", "yellow"), ("Due", "dim")],
        rows,
    )


@credits.command("pay")
@click.argument("credit_id", type=int)
@click.option("--amount", "-a", required=True, type=float, help="Payment amount")
def pay_credit(credit_id, amount):
    """Record a credit payment."""
    client = PosClient()
    resp = client.post(f"/admin/credits/{credit_id}/pay", {"amount": amount})
    if resp.status_code in (200, 302):
        print_success(f"Payment of ₱{amount:.2f} recorded for credit #{credit_id}")
    else:
        data = parse_json_or_html(resp)
        print_error(f"Payment failed: {data.get('error', resp.status_code)}")


@credits.command("history")
def credit_history():
    """View credit payment history."""
    client = PosClient()
    resp = client.get("/admin/credits/history")
    data = parse_json_or_html(resp)

    if "error" in data:
        print_error(data["error"])
        return

    items = data if isinstance(data, list) else data.get("data", data.get("payments", []))
    if not items:
        click.echo("No payment history.")
        return

    rows = []
    for p in items:
        rows.append([
            str(p.get("id", "")),
            str(p.get("credit_id", "")),
            f"₱{p.get('amount', 0):.2f}",
            p.get("created_at", "-")[:16],
        ])

    print_table(
        "Credit Payments",
        [("ID", "cyan"), ("Credit", "white"), ("Amount", "green"), ("Date", "dim")],
        rows,
    )


@credits.command("export")
@click.option("--output", "-o", default="credits_export.csv", help="Output file path")
def export_credits(output):
    """Export credit data."""
    client = PosClient()
    resp = client.get("/admin/credits/export")
    if resp.status_code == 200:
        with open(output, "wb") as f:
            f.write(resp.content)
        print_success(f"Credits exported to {output}")
    else:
        print_error(f"Export failed (HTTP {resp.status_code})")

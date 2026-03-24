"""Supplier and purchase management commands."""

import click

from ..client import PosClient
from ..utils import parse_json_or_html, print_error, print_success, print_table


@click.group()
def suppliers():
    """Supplier and purchase order management."""
    pass


@suppliers.command("list")
def list_suppliers():
    """List all suppliers."""
    client = PosClient()
    resp = client.get("/admin/suppliers")
    data = parse_json_or_html(resp)

    if "error" in data:
        print_error(data["error"])
        return

    items = data if isinstance(data, list) else data.get("data", data.get("suppliers", []))
    if not items:
        click.echo("No suppliers found.")
        return

    rows = []
    for s in items:
        rows.append([
            str(s.get("id", "")),
            s.get("name", ""),
            s.get("contact", s.get("phone", "-")),
            s.get("email", "-"),
        ])

    print_table("Suppliers", [("ID", "cyan"), ("Name", "white"), ("Contact", "dim"), ("Email", "dim")], rows)


@suppliers.command("create")
@click.option("--name", "-n", required=True, help="Supplier name")
@click.option("--contact", "-c", default="", help="Contact info")
@click.option("--email", "-e", default="", help="Email")
@click.option("--address", "-a", default="", help="Address")
def create_supplier(name, contact, email, address):
    """Add a new supplier."""
    client = PosClient()
    resp = client.post("/admin/suppliers", {
        "name": name,
        "contact": contact,
        "email": email,
        "address": address,
    })
    if resp.status_code in (200, 201, 302):
        print_success(f"Supplier '{name}' created")
    else:
        data = parse_json_or_html(resp)
        print_error(f"Failed: {data.get('error', data.get('errors', resp.status_code))}")


@click.group()
def purchases():
    """Purchase order management."""
    pass


@purchases.command("list")
def list_purchases():
    """List purchase orders."""
    client = PosClient()
    resp = client.get("/admin/purchases")
    data = parse_json_or_html(resp)

    if "error" in data:
        print_error(data["error"])
        return

    items = data if isinstance(data, list) else data.get("data", data.get("purchases", []))
    if not items:
        click.echo("No purchase orders found.")
        return

    rows = []
    for p in items:
        supplier = p.get("supplier", {}) if isinstance(p.get("supplier"), dict) else {}
        rows.append([
            str(p.get("id", "")),
            supplier.get("name", str(p.get("supplier_id", "-"))),
            f"₱{p.get('total', 0):.2f}",
            p.get("status", "-"),
            p.get("created_at", "-")[:10],
        ])

    print_table(
        "Purchase Orders",
        [("ID", "cyan"), ("Supplier", "white"), ("Total", "green"), ("Status", "yellow"), ("Date", "dim")],
        rows,
    )

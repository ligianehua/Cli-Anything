"""Inventory management commands."""

import click

from ..client import PosClient
from ..utils import parse_json_or_html, print_error, print_success, print_table


@click.group()
def inventory():
    """Inventory and stock management."""
    pass


@inventory.command("list")
@click.option("--low-stock", is_flag=True, help="Show only low-stock items")
@click.option("--search", "-s", default=None, help="Search by product name")
def list_inventory(low_stock, search):
    """View current inventory levels."""
    client = PosClient()
    params = {}
    if low_stock:
        params["low_stock"] = 1
    if search:
        params["search"] = search
    resp = client.get("/admin/inventory", params=params)
    data = parse_json_or_html(resp)

    if "error" in data:
        print_error(data["error"])
        return

    items = data if isinstance(data, list) else data.get("data", data.get("inventory", []))
    if not items:
        click.echo("No inventory records found.")
        return

    rows = []
    for item in items:
        product = item.get("product", {}) if isinstance(item.get("product"), dict) else {}
        qty = item.get("quantity", item.get("stock", "-"))
        reorder = item.get("reorder_point", "-")
        name = product.get("name", item.get("name", "-"))
        sku = product.get("sku", item.get("sku", "-"))
        rows.append([str(item.get("id", "")), name, sku, str(qty), str(reorder)])

    print_table(
        "Inventory",
        [("ID", "cyan"), ("Product", "white"), ("SKU", "dim"), ("Qty", "yellow"), ("Reorder Pt", "red")],
        rows,
    )


@inventory.command("adjust")
@click.option("--product-id", "-p", required=True, type=int, help="Product ID")
@click.option("--quantity", "-q", required=True, type=int, help="Adjustment quantity (+ or -)")
@click.option("--type", "-t", "adj_type", type=click.Choice(["spoilage", "theft", "internal_use", "audit"]), required=True, help="Adjustment reason")
@click.option("--notes", "-n", default="", help="Notes")
def adjust_stock(product_id, quantity, adj_type, notes):
    """Manually adjust stock levels."""
    client = PosClient()
    resp = client.post("/admin/inventory/adjust", {
        "product_id": product_id,
        "quantity": quantity,
        "type": adj_type,
        "notes": notes,
    })
    if resp.status_code in (200, 302):
        print_success(f"Stock adjusted: product #{product_id} by {quantity:+d} ({adj_type})")
    else:
        data = parse_json_or_html(resp)
        print_error(f"Failed: {data.get('error', data.get('errors', resp.status_code))}")


@inventory.command("history")
@click.option("--product-id", "-p", type=int, help="Filter by product ID")
def history(product_id):
    """View stock adjustment history."""
    client = PosClient()
    params = {}
    if product_id:
        params["product_id"] = product_id
    resp = client.get("/admin/inventory/history", params=params)
    data = parse_json_or_html(resp)

    if "error" in data:
        print_error(data["error"])
        return

    items = data if isinstance(data, list) else data.get("data", data.get("adjustments", []))
    if not items:
        click.echo("No adjustment history.")
        return

    rows = []
    for a in items:
        rows.append([
            str(a.get("id", "")),
            str(a.get("product_id", "")),
            str(a.get("quantity", "")),
            a.get("type", "-"),
            a.get("notes", "-"),
            a.get("created_at", "-"),
        ])

    print_table(
        "Stock Adjustments",
        [("ID", "cyan"), ("Product", "white"), ("Qty", "yellow"), ("Type", "magenta"), ("Notes", "dim"), ("Date", "dim")],
        rows,
    )


@inventory.command("export")
@click.option("--output", "-o", default="inventory_export.csv", help="Output file path")
def export_inventory(output):
    """Export inventory data to file."""
    client = PosClient()
    resp = client.get("/admin/inventory/export")
    if resp.status_code == 200:
        with open(output, "wb") as f:
            f.write(resp.content)
        print_success(f"Inventory exported to {output}")
    else:
        print_error(f"Export failed (HTTP {resp.status_code})")

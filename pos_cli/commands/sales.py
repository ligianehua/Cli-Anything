"""Sales and transaction commands."""

import json

import click

from ..client import PosClient
from ..utils import parse_json_or_html, print_dict, print_error, print_success, print_table


@click.group()
def sales():
    """Sales transactions and POS operations."""
    pass


@sales.command("new")
@click.option("--items", "-i", required=True, help='Items as JSON: [{"product_id":1,"quantity":2}, ...]')
@click.option("--payment", "-p", type=click.Choice(["cash", "digital", "credit"]), default="cash", help="Payment method")
@click.option("--customer-id", "-c", type=int, help="Customer ID (required for credit)")
@click.option("--amount-paid", "-a", type=float, help="Amount tendered (cash)")
def new_sale(items, payment, customer_id, amount_paid):
    """Process a new sale transaction."""
    try:
        item_list = json.loads(items)
    except json.JSONDecodeError:
        print_error("Invalid JSON for --items. Use format: '[{\"product_id\":1,\"quantity\":2}]'")
        return

    client = PosClient()
    payload = {
        "items": item_list,
        "payment_method": payment,
    }
    if customer_id:
        payload["customer_id"] = customer_id
    if amount_paid is not None:
        payload["amount_paid"] = amount_paid

    resp = client.post("/cashier/transaction", payload)
    data = parse_json_or_html(resp)

    if resp.status_code in (200, 201):
        sale_id = data.get("sale", {}).get("id", data.get("id", "?"))
        total = data.get("sale", {}).get("total", data.get("total", "?"))
        change = data.get("change", 0)
        print_success(f"Sale #{sale_id} completed — Total: ₱{total}, Change: ₱{change}")
    else:
        print_error(f"Transaction failed: {data.get('error', data.get('message', resp.status_code))}")


@sales.command("list")
@click.option("--date", "-d", help="Filter by date (YYYY-MM-DD)")
@click.option("--limit", "-l", type=int, default=20, help="Number of results")
def list_sales(date, limit):
    """List recent transactions."""
    client = PosClient()
    params = {"per_page": limit}
    if date:
        params["date"] = date
    resp = client.get("/admin/transactions", params=params)
    data = parse_json_or_html(resp)

    if "error" in data:
        print_error(data["error"])
        return

    items = data if isinstance(data, list) else data.get("data", data.get("transactions", []))
    if not items:
        click.echo("No transactions found.")
        return

    rows = []
    for s in items:
        rows.append([
            str(s.get("id", "")),
            s.get("created_at", "-")[:16],
            f"₱{s.get('total', 0):.2f}",
            s.get("payment_method", "-"),
            s.get("status", "completed"),
        ])

    print_table(
        "Transactions",
        [("ID", "cyan"), ("Date", "dim"), ("Total", "green"), ("Payment", "yellow"), ("Status", "white")],
        rows,
    )


@sales.command("show")
@click.argument("sale_id", type=int)
def show_sale(sale_id):
    """Show sale/receipt details."""
    client = PosClient()
    resp = client.get(f"/cashier/receipt/{sale_id}")
    data = parse_json_or_html(resp)

    if "error" in data:
        print_error(data["error"])
        return

    sale = data.get("sale", data)
    print_dict("Sale Details", {
        "Sale ID": sale.get("id"),
        "Date": sale.get("created_at"),
        "Total": f"₱{sale.get('total', 0):.2f}",
        "Payment": sale.get("payment_method"),
        "Cashier": sale.get("user", {}).get("name") if isinstance(sale.get("user"), dict) else sale.get("user_id"),
        "Customer": sale.get("customer", {}).get("name") if isinstance(sale.get("customer"), dict) else sale.get("customer_id", "-"),
    })

    items = sale.get("items", sale.get("sale_items", []))
    if items:
        rows = []
        for item in items:
            product = item.get("product", {}) if isinstance(item.get("product"), dict) else {}
            rows.append([
                product.get("name", str(item.get("product_id", ""))),
                str(item.get("quantity", "")),
                f"₱{item.get('price', 0):.2f}",
                f"₱{item.get('subtotal', item.get('quantity', 0) * item.get('price', 0)):.2f}",
            ])
        print_table("Items", [("Product", "white"), ("Qty", "yellow"), ("Price", "green"), ("Subtotal", "green")], rows)


@sales.command("return")
@click.argument("sale_id", type=int)
@click.option("--items", "-i", help='Items to return as JSON: [{"sale_item_id":1,"quantity":1}]')
@click.option("--reason", "-r", default="", help="Return reason")
def return_sale(sale_id, items, reason):
    """Process a sales return."""
    client = PosClient()
    payload = {"reason": reason}
    if items:
        try:
            payload["items"] = json.loads(items)
        except json.JSONDecodeError:
            print_error("Invalid JSON for --items")
            return

    resp = client.post(f"/admin/transactions/{sale_id}/return", payload)
    if resp.status_code in (200, 302):
        print_success(f"Return processed for sale #{sale_id}")
    else:
        data = parse_json_or_html(resp)
        print_error(f"Return failed: {data.get('error', resp.status_code)}")

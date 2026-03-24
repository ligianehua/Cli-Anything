"""Product management commands."""

import click

from ..client import PosClient
from ..utils import parse_json_or_html, print_error, print_success, print_table, print_dict


@click.group()
def products():
    """Product management (CRUD, import, pricing)."""
    pass


@products.command("list")
@click.option("--search", "-s", default=None, help="Search by name or SKU")
@click.option("--category", "-c", default=None, help="Filter by category")
def list_products(search, category):
    """List all products."""
    client = PosClient()
    params = {}
    if search:
        params["search"] = search
    if category:
        params["category"] = category
    resp = client.get("/admin/products", params=params)
    data = parse_json_or_html(resp)

    if "error" in data:
        print_error(data["error"])
        return

    items = data if isinstance(data, list) else data.get("data", data.get("products", []))
    if not items:
        click.echo("No products found.")
        return

    rows = []
    for p in items:
        rows.append([
            str(p.get("id", "")),
            p.get("name", ""),
            p.get("sku", "-"),
            f"₱{p.get('price', 0):.2f}",
            str(p.get("stock", p.get("inventory", {}).get("quantity", "-"))),
            p.get("category", {}).get("name", "-") if isinstance(p.get("category"), dict) else str(p.get("category_id", "-")),
        ])

    print_table(
        "Products",
        [("ID", "cyan"), ("Name", "white"), ("SKU", "dim"), ("Price", "green"), ("Stock", "yellow"), ("Category", "magenta")],
        rows,
    )


@products.command("show")
@click.argument("product_id", type=int)
def show_product(product_id):
    """Show product details."""
    client = PosClient()
    resp = client.get(f"/admin/products/{product_id}")
    data = parse_json_or_html(resp)
    if "error" in data:
        print_error(data["error"])
        return

    p = data.get("product", data)
    print_dict("Product Details", {
        "ID": p.get("id"),
        "Name": p.get("name"),
        "SKU": p.get("sku"),
        "Price": f"₱{p.get('price', 0):.2f}",
        "Cost": f"₱{p.get('cost', 0):.2f}",
        "Category": p.get("category", {}).get("name") if isinstance(p.get("category"), dict) else p.get("category_id"),
        "Unit": p.get("unit"),
        "Expiration": p.get("expiration_date", "-"),
        "Created": p.get("created_at", "-"),
    })


@products.command("create")
@click.option("--name", "-n", required=True, help="Product name")
@click.option("--sku", required=True, help="SKU code")
@click.option("--price", "-p", required=True, type=float, help="Selling price")
@click.option("--cost", type=float, default=0, help="Cost price")
@click.option("--category-id", "-c", type=int, help="Category ID")
@click.option("--unit", default="pcs", help="Unit of measurement")
def create_product(name, sku, price, cost, category_id, unit):
    """Create a new product."""
    client = PosClient()
    payload = {
        "name": name,
        "sku": sku,
        "price": price,
        "cost": cost,
        "unit": unit,
    }
    if category_id:
        payload["category_id"] = category_id

    resp = client.post("/admin/products", payload)
    if resp.status_code in (200, 201, 302):
        print_success(f"Product '{name}' created")
    else:
        data = parse_json_or_html(resp)
        print_error(f"Failed: {data.get('error', data.get('errors', resp.status_code))}")


@products.command("update")
@click.argument("product_id", type=int)
@click.option("--name", "-n", help="Product name")
@click.option("--sku", help="SKU code")
@click.option("--price", "-p", type=float, help="Selling price")
@click.option("--cost", type=float, help="Cost price")
@click.option("--category-id", "-c", type=int, help="Category ID")
def update_product(product_id, name, sku, price, cost, category_id):
    """Update a product."""
    client = PosClient()
    payload = {}
    if name:
        payload["name"] = name
    if sku:
        payload["sku"] = sku
    if price is not None:
        payload["price"] = price
    if cost is not None:
        payload["cost"] = cost
    if category_id:
        payload["category_id"] = category_id

    if not payload:
        print_error("No fields to update. Use --name, --price, etc.")
        return

    resp = client.post(f"/admin/products/{product_id}", {**payload, "_method": "PUT"})
    if resp.status_code in (200, 302):
        print_success(f"Product #{product_id} updated")
    else:
        data = parse_json_or_html(resp)
        print_error(f"Failed: {data.get('error', data.get('errors', resp.status_code))}")


@products.command("delete")
@click.argument("product_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this product?")
def delete_product(product_id):
    """Delete a product (soft delete)."""
    client = PosClient()
    resp = client.delete(f"/admin/products/{product_id}")
    if resp.status_code in (200, 302):
        print_success(f"Product #{product_id} deleted")
    else:
        print_error(f"Failed (HTTP {resp.status_code})")


@products.command("import")
@click.argument("file_path", type=click.Path(exists=True))
def import_products(file_path):
    """Bulk import products from a CSV/Excel file."""
    client = PosClient()
    with open(file_path, "rb") as f:
        resp = client.post("/admin/products/import", files={"file": f})
    if resp.status_code in (200, 302):
        print_success(f"Products imported from {file_path}")
    else:
        data = parse_json_or_html(resp)
        print_error(f"Import failed: {data.get('error', resp.status_code)}")

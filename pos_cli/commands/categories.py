"""Category management commands."""

import click

from ..client import PosClient
from ..utils import parse_json_or_html, print_error, print_success, print_table


@click.group()
def categories():
    """Product category management."""
    pass


@categories.command("list")
def list_categories():
    """List all categories."""
    client = PosClient()
    resp = client.get("/admin/categories")
    data = parse_json_or_html(resp)
    if "error" in data:
        print_error(data["error"])
        return

    items = data if isinstance(data, list) else data.get("data", data.get("categories", []))
    if not items:
        click.echo("No categories found.")
        return

    rows = [[str(c.get("id", "")), c.get("name", ""), str(c.get("products_count", "-"))] for c in items]
    print_table("Categories", [("ID", "cyan"), ("Name", "white"), ("Products", "yellow")], rows)


@categories.command("create")
@click.option("--name", "-n", required=True, help="Category name")
def create_category(name):
    """Create a new category."""
    client = PosClient()
    resp = client.post("/admin/categories", {"name": name})
    if resp.status_code in (200, 201, 302):
        print_success(f"Category '{name}' created")
    else:
        data = parse_json_or_html(resp)
        print_error(f"Failed: {data.get('error', data.get('errors', resp.status_code))}")

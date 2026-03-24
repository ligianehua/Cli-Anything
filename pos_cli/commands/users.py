"""User management commands."""

import click

from ..client import PosClient
from ..utils import parse_json_or_html, print_dict, print_error, print_success, print_table


@click.group()
def users():
    """User and role management."""
    pass


@users.command("list")
def list_users():
    """List all users."""
    client = PosClient()
    resp = client.get("/admin/users")
    data = parse_json_or_html(resp)

    if "error" in data:
        print_error(data["error"])
        return

    items = data if isinstance(data, list) else data.get("data", data.get("users", []))
    if not items:
        click.echo("No users found.")
        return

    rows = []
    for u in items:
        rows.append([
            str(u.get("id", "")),
            u.get("name", ""),
            u.get("email", ""),
            u.get("role", "-"),
            "Active" if u.get("is_active", True) else "Inactive",
        ])

    print_table(
        "Users",
        [("ID", "cyan"), ("Name", "white"), ("Email", "dim"), ("Role", "magenta"), ("Status", "green")],
        rows,
    )


@users.command("toggle")
@click.argument("user_id", type=int)
def toggle_user(user_id):
    """Enable or disable a user."""
    client = PosClient()
    resp = client.post(f"/admin/users/{user_id}/toggle")
    if resp.status_code in (200, 302):
        print_success(f"User #{user_id} status toggled")
    else:
        data = parse_json_or_html(resp)
        print_error(f"Failed: {data.get('error', resp.status_code)}")


@users.command("restore")
@click.argument("user_id", type=int)
def restore_user(user_id):
    """Restore an archived (soft-deleted) user."""
    client = PosClient()
    resp = client.post(f"/admin/users/{user_id}/restore")
    if resp.status_code in (200, 302):
        print_success(f"User #{user_id} restored")
    else:
        data = parse_json_or_html(resp)
        print_error(f"Failed: {data.get('error', resp.status_code)}")


@users.command("delete")
@click.argument("user_id", type=int)
@click.confirmation_option(prompt="Are you sure? This permanently deletes the user.")
def delete_user(user_id):
    """Permanently delete a user."""
    client = PosClient()
    resp = client.delete(f"/admin/users/{user_id}/force-delete")
    if resp.status_code in (200, 302):
        print_success(f"User #{user_id} permanently deleted")
    else:
        data = parse_json_or_html(resp)
        print_error(f"Failed: {data.get('error', resp.status_code)}")

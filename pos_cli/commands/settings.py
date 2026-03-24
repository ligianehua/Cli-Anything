"""System settings and admin commands."""

import click

from ..client import PosClient
from ..utils import parse_json_or_html, print_dict, print_error, print_success


@click.group()
def settings():
    """System settings, backup, and admin tools."""
    pass


@settings.command("show")
def show_settings():
    """Show current system settings."""
    client = PosClient()
    resp = client.get("/admin/settings")
    data = parse_json_or_html(resp)

    if "error" in data:
        print_error(data["error"])
        return

    s = data.get("settings", data)
    if isinstance(s, dict):
        print_dict("System Settings", {k: v for k, v in s.items() if not isinstance(v, (list, dict))})
    elif isinstance(s, list):
        print_dict("System Settings", {item.get("key", "?"): item.get("value", "-") for item in s})


@settings.command("update")
@click.option("--key", "-k", required=True, help="Setting key")
@click.option("--value", "-v", required=True, help="Setting value")
def update_setting(key, value):
    """Update a system setting."""
    client = PosClient()
    resp = client.post("/admin/settings", {key: value})
    if resp.status_code in (200, 302):
        print_success(f"Setting '{key}' updated to '{value}'")
    else:
        data = parse_json_or_html(resp)
        print_error(f"Failed: {data.get('error', resp.status_code)}")


@settings.command("backup")
@click.option("--output", "-o", default="pos_backup.sql", help="Output file path")
def backup(output):
    """Download database backup."""
    client = PosClient()
    resp = client.get("/admin/settings/backup")
    if resp.status_code == 200:
        with open(output, "wb") as f:
            f.write(resp.content)
        print_success(f"Backup saved to {output}")
    else:
        print_error(f"Backup failed (HTTP {resp.status_code})")


@settings.command("restore")
@click.argument("file_path", type=click.Path(exists=True))
@click.confirmation_option(prompt="This will overwrite current data. Are you sure?")
def restore(file_path):
    """Restore database from backup file."""
    client = PosClient()
    with open(file_path, "rb") as f:
        resp = client.post("/admin/settings/restore", files={"backup": f})
    if resp.status_code in (200, 302):
        print_success("Database restored successfully")
    else:
        data = parse_json_or_html(resp)
        print_error(f"Restore failed: {data.get('error', resp.status_code)}")


@settings.command("logs")
@click.option("--limit", "-l", type=int, default=20, help="Number of log entries")
def view_logs(limit):
    """View activity logs."""
    client = PosClient()
    resp = client.get("/admin/logs", params={"per_page": limit})
    data = parse_json_or_html(resp)

    if "error" in data:
        print_error(data["error"])
        return

    from ..utils import print_table
    items = data if isinstance(data, list) else data.get("data", data.get("logs", []))
    if not items:
        click.echo("No logs found.")
        return

    rows = []
    for log in items:
        user = log.get("user", {}) if isinstance(log.get("user"), dict) else {}
        rows.append([
            log.get("created_at", "-")[:16],
            user.get("name", str(log.get("user_id", "-"))),
            log.get("action", log.get("description", "-")),
            log.get("ip_address", "-"),
        ])

    print_table(
        "Activity Logs",
        [("Time", "dim"), ("User", "cyan"), ("Action", "white"), ("IP", "dim")],
        rows,
    )

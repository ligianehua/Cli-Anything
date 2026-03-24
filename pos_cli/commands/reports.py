"""Reporting commands."""

import click

from ..client import PosClient
from ..utils import parse_json_or_html, print_dict, print_error, print_success, print_table


@click.group()
def reports():
    """Reports and analytics."""
    pass


@reports.command("dashboard")
def dashboard():
    """Show dashboard analytics summary."""
    client = PosClient()
    resp = client.get("/admin/dashboard")
    data = parse_json_or_html(resp)

    if "error" in data:
        print_error(data["error"])
        return

    metrics = data.get("metrics", data)
    print_dict("Dashboard", {
        "Today's Sales": f"₱{metrics.get('today_sales', metrics.get('gross_sales', 0)):.2f}",
        "Net Sales": f"₱{metrics.get('net_sales', 0):.2f}",
        "Transactions": metrics.get("transaction_count", metrics.get("transactions", 0)),
        "Profit": f"₱{metrics.get('profit', 0):.2f}",
        "Low Stock Items": metrics.get("low_stock_count", metrics.get("low_stock", 0)),
        "Outstanding Credits": f"₱{metrics.get('outstanding_credits', 0):.2f}",
    })


@reports.command("sales")
@click.option("--from", "from_date", help="Start date (YYYY-MM-DD)")
@click.option("--to", "to_date", help="End date (YYYY-MM-DD)")
def sales_report(from_date, to_date):
    """Generate sales report."""
    client = PosClient()
    params = {"type": "sales"}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    resp = client.get("/admin/reports", params=params)
    data = parse_json_or_html(resp)

    if "error" in data:
        print_error(data["error"])
        return

    report = data.get("report", data)
    if isinstance(report, dict):
        print_dict("Sales Report", {k: v for k, v in report.items() if not isinstance(v, (list, dict))})


@reports.command("inventory")
def inventory_report():
    """Generate inventory report."""
    client = PosClient()
    resp = client.get("/admin/reports/inventory")
    data = parse_json_or_html(resp)

    if "error" in data:
        print_error(data["error"])
        return

    items = data if isinstance(data, list) else data.get("data", data.get("inventory", []))
    if not items:
        click.echo("No inventory data.")
        return

    rows = []
    for item in items:
        rows.append([
            item.get("name", "-"),
            str(item.get("quantity", item.get("stock", "-"))),
            f"₱{item.get('value', 0):.2f}" if item.get("value") else "-",
        ])

    print_table("Inventory Report", [("Product", "white"), ("Stock", "yellow"), ("Value", "green")], rows)


@reports.command("forecast")
def forecast():
    """Show sales forecast."""
    client = PosClient()
    resp = client.get("/admin/reports/forecast")
    data = parse_json_or_html(resp)

    if "error" in data:
        print_error(data["error"])
        return

    forecast_data = data.get("forecast", data)
    if isinstance(forecast_data, dict):
        print_dict("Sales Forecast", {k: v for k, v in forecast_data.items() if not isinstance(v, (list, dict))})
    elif isinstance(forecast_data, list):
        rows = [[str(f.get("date", "")), f"₱{f.get('predicted', 0):.2f}"] for f in forecast_data]
        print_table("Sales Forecast", [("Date", "dim"), ("Predicted", "green")], rows)


@reports.command("export")
@click.option("--type", "-t", "report_type", type=click.Choice(["sales", "inventory", "credits"]), default="sales")
@click.option("--format", "-f", "fmt", type=click.Choice(["csv", "pdf", "excel"]), default="csv")
@click.option("--output", "-o", default=None, help="Output file path")
def export_report(report_type, fmt, output):
    """Export report to file."""
    if not output:
        output = f"report_{report_type}.{fmt}"
    client = PosClient()
    resp = client.get("/admin/reports/export", params={"type": report_type, "format": fmt})
    if resp.status_code == 200:
        with open(output, "wb") as f:
            f.write(resp.content)
        print_success(f"Report exported to {output}")
    else:
        print_error(f"Export failed (HTTP {resp.status_code})")

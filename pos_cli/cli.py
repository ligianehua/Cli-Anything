"""VeraPOS CLI — Command line interface for the VeraPOS system.

Usage:
    pos login                          Login to the POS system
    pos products list                  List all products
    pos sales new -i '[...]' -p cash   Process a sale
    pos register open -b 5000          Open cash register
    pos reports dashboard              View dashboard metrics
    pos --help                         Show all commands
"""

import click

from . import __version__
from .commands.auth import auth
from .commands.categories import categories
from .commands.customers import credits, customers
from .commands.inventory import inventory
from .commands.products import products
from .commands.register import register
from .commands.reports import reports
from .commands.sales import sales
from .commands.settings import settings
from .commands.suppliers import purchases, suppliers
from .commands.users import users


@click.group()
@click.version_option(__version__, prog_name="pos-cli")
def cli():
    """VeraPOS CLI — Manage your Point of Sale system from the terminal.

    \b
    Quick start:
      1. pos set-url http://localhost:8000
      2. pos login -e admin@example.com -p password
      3. pos products list
      4. pos sales new -i '[{"product_id":1,"quantity":2}]' -p cash
    """
    pass


# Auth commands (flattened to top level for convenience)
cli.add_command(auth.commands["login"], "login")
cli.add_command(auth.commands["logout"], "logout")
cli.add_command(auth.commands["set-url"], "set-url")
cli.add_command(auth.commands["status"], "auth-status")

# Resource groups
cli.add_command(products)
cli.add_command(categories)
cli.add_command(inventory)
cli.add_command(sales)
cli.add_command(customers)
cli.add_command(credits)
cli.add_command(register)
cli.add_command(reports)
cli.add_command(users)
cli.add_command(suppliers)
cli.add_command(purchases)
cli.add_command(settings)


def main():
    cli()


if __name__ == "__main__":
    main()

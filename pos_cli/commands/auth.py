"""Authentication commands."""

import click
from rich.prompt import Prompt

from ..client import PosClient
from ..config import clear_session, get_base_url, load_config, save_config
from ..utils import print_error, print_success


@click.group()
def auth():
    """Authentication and configuration."""
    pass


@auth.command()
@click.option("--email", "-e", prompt="Email", help="Login email")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Login password")
def login(email, password):
    """Login to the POS system."""
    client = PosClient()
    result = client.login(email, password)
    if "error" in result:
        print_error(f"Login failed: {result['error']}")
        raise SystemExit(1)
    print_success(f"Logged in as {email}")


@auth.command()
def logout():
    """Logout from the POS system."""
    client = PosClient()
    client.logout()
    print_success("Logged out")


@auth.command()
@click.argument("url")
def set_url(url):
    """Set the POS server URL (e.g. http://localhost:8000)."""
    config = load_config()
    config["base_url"] = url.rstrip("/")
    save_config(config)
    print_success(f"Server URL set to {url}")


@auth.command()
def status():
    """Show current authentication and config status."""
    from ..config import load_session
    config = load_config()
    session = load_session()
    click.echo(f"Server URL: {get_base_url()}")
    click.echo(f"Session:    {'active' if session else 'none'}")

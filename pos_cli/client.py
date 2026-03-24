"""HTTP client for VeraPOS API."""

import sys

import requests
from rich.console import Console

from .config import clear_session, get_base_url, load_session, save_session

console = Console(stderr=True)


class PosClient:
    """HTTP client that handles authentication and CSRF for the Laravel POS app."""

    def __init__(self):
        self.base_url = get_base_url().rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
        })
        self._restore_session()

    def _restore_session(self):
        saved = load_session()
        if saved and "cookies" in saved:
            for name, value in saved["cookies"].items():
                self.session.cookies.set(name, value)

    def _persist_session(self):
        save_session({
            "cookies": dict(self.session.cookies),
        })

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _fetch_csrf(self):
        """Get CSRF token from Laravel by fetching the login page."""
        resp = self.session.get(self._url("/login"), headers={"Accept": "text/html"})
        resp.raise_for_status()
        token = self.session.cookies.get("XSRF-TOKEN")
        if token:
            from urllib.parse import unquote
            self.session.headers["X-XSRF-TOKEN"] = unquote(token)

    def _ensure_csrf(self):
        if "X-XSRF-TOKEN" not in self.session.headers:
            self._fetch_csrf()

    def login(self, email: str, password: str) -> dict:
        self._fetch_csrf()
        resp = self.session.post(self._url("/login"), json={
            "email": email,
            "password": password,
        })
        if resp.status_code == 422:
            return {"error": resp.json().get("errors", resp.json())}
        if resp.status_code == 302 or resp.ok:
            self._persist_session()
            return {"success": True, "redirect": resp.headers.get("Location", "/")}
        return {"error": f"Login failed (HTTP {resp.status_code})"}

    def logout(self) -> dict:
        self._ensure_csrf()
        resp = self.session.post(self._url("/logout"))
        clear_session()
        return {"success": True}

    def get(self, path: str, params: dict | None = None) -> requests.Response:
        self._ensure_csrf()
        resp = self.session.get(self._url(path), params=params)
        if resp.status_code == 401:
            console.print("[red]Not authenticated. Run: pos login[/red]")
            sys.exit(1)
        return resp

    def post(self, path: str, data: dict | None = None, files=None) -> requests.Response:
        self._ensure_csrf()
        if files:
            resp = self.session.post(self._url(path), data=data, files=files)
        else:
            resp = self.session.post(self._url(path), json=data)
        if resp.status_code == 401:
            console.print("[red]Not authenticated. Run: pos login[/red]")
            sys.exit(1)
        return resp

    def delete(self, path: str) -> requests.Response:
        self._ensure_csrf()
        resp = self.session.delete(self._url(path))
        if resp.status_code == 401:
            console.print("[red]Not authenticated. Run: pos login[/red]")
            sys.exit(1)
        return resp

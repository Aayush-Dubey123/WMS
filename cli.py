#!/usr/bin/env python3
"""
Whitfield WMS CLI — Typer + httpx client for the WMS backend API.

Usage:
    python cli.py --help
    python cli.py login --email owner@example.com --password secret
    python cli.py orders create --order-id ORD-001 --customer "Jane Doe" --warehouse-id <id>
"""

import csv
import json
import os
import sys
from pathlib import Path
from typing import Optional

import httpx
import typer
from rich.console import Console
from rich.table import Table

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CONFIG_PATH = Path.home() / ".wms" / "config.json"
API_BASE = os.environ.get("WMS_API_BASE", "http://127.0.0.1:8000")

app = typer.Typer(help="Whitfield WMS command-line interface", add_completion=False)
console = Console()


def _save_config(data: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(data, indent=2))


def _load_config() -> dict:
    if not CONFIG_PATH.exists():
        console.print("[red]Not logged in. Run: python cli.py login[/red]")
        raise typer.Exit(1)
    return json.loads(CONFIG_PATH.read_text())


def _token() -> str:
    return _load_config()["access_token"]


def _headers() -> dict:
    return {"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"}


def _get(path: str, params: Optional[dict] = None) -> dict:
    try:
        r = httpx.get(f"{API_BASE}{path}", headers=_headers(), params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        console.print(f"[red]HTTP {e.response.status_code}: {e.response.text}[/red]")
        raise typer.Exit(1)
    except httpx.ConnectError:
        console.print(f"[red]Cannot reach API at {API_BASE}. Is the server running?[/red]")
        raise typer.Exit(1)


def _post(path: str, body: dict, extra_headers: Optional[dict] = None) -> dict:
    headers = {**_headers(), **(extra_headers or {})}
    try:
        r = httpx.post(f"{API_BASE}{path}", headers=headers, json=body, timeout=15)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        console.print(f"[red]HTTP {e.response.status_code}: {e.response.text}[/red]")
        raise typer.Exit(1)
    except httpx.ConnectError:
        console.print(f"[red]Cannot reach API at {API_BASE}. Is the server running?[/red]")
        raise typer.Exit(1)


def _table(*cols: str) -> Table:
    t = Table(show_header=True, header_style="bold cyan")
    for c in cols:
        t.add_column(c)
    return t


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@app.command()
def login(
    email: str = typer.Option(..., prompt=True, help="Account email"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Account password"),
):
    """Authenticate and store JWT in ~/.wms/config.json."""
    try:
        r = httpx.post(
            f"{API_BASE}/auth/login",
            json={"email": email, "password": password},
            timeout=15,
        )
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        console.print(f"[red]Login failed: {e.response.status_code} {e.response.text}[/red]")
        raise typer.Exit(1)
    except httpx.ConnectError:
        console.print(f"[red]Cannot reach API at {API_BASE}[/red]")
        raise typer.Exit(1)

    data = r.json()
    _save_config({
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token", ""),
        "email": email,
        "api_base": API_BASE,
    })
    console.print(f"[green]Logged in as {email}. Token saved to {CONFIG_PATH}[/green]")


# ---------------------------------------------------------------------------
# Inbox sub-app
# ---------------------------------------------------------------------------

inbox_app = typer.Typer(help="Inbox & shipment announcement commands")
app.add_typer(inbox_app, name="inbox")


@inbox_app.command("list")
def inbox_list(
    status: Optional[str] = typer.Option(None, help="Filter by status"),
    limit: int = typer.Option(20, help="Max records"),
):
    """List inbox shipment announcements."""
    params = {"skip": 0, "limit": limit}
    if status:
        params["status_filter"] = status
    data = _get("/inbox", params=params)
    records = data if isinstance(data, list) else data.get("shipments", [])
    t = _table("ID", "Tracking", "Status", "Carrier", "Created")
    for r in records:
        t.add_row(
            str(r.get("id", "—")),
            r.get("tracking_number", "—"),
            r.get("status", "—"),
            r.get("carrier", "—"),
            r.get("created_at", "—"),
        )
    console.print(t)


@inbox_app.command("accept")
def inbox_accept(shipment_id: str = typer.Argument(..., help="Inbox shipment ID")):
    """Accept an inbox shipment."""
    data = _post(f"/inbox/{shipment_id}/accept", {})
    console.print(f"[green]Accepted:[/green] {data.get('status', data)}")


@inbox_app.command("decline")
def inbox_decline(shipment_id: str = typer.Argument(..., help="Inbox shipment ID")):
    """Decline an inbox shipment."""
    data = _post(f"/inbox/{shipment_id}/decline", {})
    console.print(f"[yellow]Declined:[/yellow] {data.get('status', data)}")


# ---------------------------------------------------------------------------
# Arrivals sub-app
# ---------------------------------------------------------------------------

arrivals_app = typer.Typer(help="Inbound arrival commands")
app.add_typer(arrivals_app, name="arrivals")


@arrivals_app.command("create")
def arrivals_create(
    warehouse_id: str = typer.Option(..., help="Warehouse ID"),
    tracking: Optional[str] = typer.Option(None, help="Carrier tracking number"),
    no_ticket: bool = typer.Option(False, help="Flag as no-ticket arrival"),
):
    """Log a physical parcel arrival and generate a ticket."""
    body = {
        "warehouse_id": warehouse_id,
        "no_ticket_arrival": no_ticket,
    }
    if tracking:
        body["tracking_number"] = tracking
    data = _post("/arrivals", body)
    console.print(f"[green]Ticket created:[/green] {data.get('ticket_id', data)}")


# ---------------------------------------------------------------------------
# Tickets sub-app
# ---------------------------------------------------------------------------

tickets_app = typer.Typer(help="Ticket, inspection & storage commands")
app.add_typer(tickets_app, name="tickets")


@tickets_app.command("log")
def tickets_log(
    ticket_id: str = typer.Argument(..., help="Ticket ID (e.g. RNO-20260814-001)"),
    barcode: str = typer.Option(..., help="Item barcode"),
    product_name: str = typer.Option(..., help="Product description"),
    weight: float = typer.Option(..., help="Item weight in kg"),
    width: float = typer.Option(0.0, help="Width in cm"),
    height: float = typer.Option(0.0, help="Height in cm"),
):
    """Log a scanned item unit under a ticket."""
    import uuid
    body = {
        "barcode": barcode,
        "product_name": product_name,
        "weight": weight,
        "width": width,
        "height": height,
    }
    data = _post(
        f"/tickets/{ticket_id}/items",
        body,
        extra_headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    console.print(f"[green]Item logged:[/green] {data.get('id', data)}")


@tickets_app.command("approve")
def tickets_approve(ticket_id: str = typer.Argument(..., help="Ticket ID")):
    """Approve ticket inspection."""
    data = _post(f"/tickets/{ticket_id}/approve", {})
    console.print(f"[green]Approved:[/green] {data.get('status', data)}")


@tickets_app.command("store")
def tickets_store(
    ticket_id: str = typer.Argument(..., help="Ticket ID"),
    location: str = typer.Option(..., help="Storage location code (e.g. A-04-12)"),
):
    """Assign a storage location to a ticket."""
    data = _post(f"/tickets/{ticket_id}/store", {"storage_location": location})
    console.print(f"[green]Stored:[/green] {data.get('status', data)}")


# ---------------------------------------------------------------------------
# Orders sub-app
# ---------------------------------------------------------------------------

orders_app = typer.Typer(help="Order & fulfillment commands")
app.add_typer(orders_app, name="orders")


@orders_app.command("create")
def orders_create(
    order_id: str = typer.Option(..., help="Order reference ID"),
    customer: str = typer.Option(..., help="Customer name"),
    warehouse_id: str = typer.Option(..., help="Warehouse ID"),
):
    """Create a new customer order."""
    body = {
        "order_id": order_id,
        "customer_name": customer,
        "warehouse_id": warehouse_id,
        "items": [],
    }
    data = _post("/orders", body)
    console.print(f"[green]Order created:[/green] {data.get('order_id', data)}")


@orders_app.command("reserve")
def orders_reserve(order_id: str = typer.Argument(..., help="Order ID")):
    """Reserve stock for an order."""
    data = _post(f"/orders/{order_id}/reserve", {})
    console.print(f"[green]Reserved:[/green] {data.get('status', data)}")


@orders_app.command("ship")
def orders_ship(order_id: str = typer.Argument(..., help="Order ID")):
    """Ship an order (marks reserved items as SOLD)."""
    data = _post(f"/orders/{order_id}/ship", {})
    console.print(f"[green]Shipped:[/green] {data.get('status', data)}")


@orders_app.command("list")
def orders_list(
    status: Optional[str] = typer.Option(None, help="Filter by status"),
    limit: int = typer.Option(20, help="Max records"),
):
    """List customer orders."""
    params = {"skip": 0, "limit": limit}
    if status:
        params["status"] = status
    data = _get("/orders", params=params)
    records = data if isinstance(data, list) else data.get("orders", [])
    t = _table("Order ID", "Customer", "Items", "Status", "Created")
    for r in records:
        t.add_row(
            r.get("order_id", "—"),
            r.get("customer_name", "—"),
            str(len(r.get("items", []))),
            r.get("status", "—"),
            r.get("created_at", "—"),
        )
    console.print(t)


# ---------------------------------------------------------------------------
# Reports sub-app
# ---------------------------------------------------------------------------

reports_app = typer.Typer(help="Reporting commands")
app.add_typer(reports_app, name="reports")


@reports_app.command("summary")
def reports_summary(date: Optional[str] = typer.Option(None, help="Target date YYYY-MM-DD")):
    """Show executive dashboard summary metrics."""
    params = {}
    if date:
        params["date"] = date
    data = _get("/reports/summary", params=params)
    t = _table("Metric", "Value")
    t.add_row("Date", str(data.get("date", "—")))
    t.add_row("Tickets Today", str(data.get("todays_tickets", "—")))
    t.add_row("Items Sold Today", str(data.get("todays_sold", "—")))
    t.add_row("Unannounced Arrivals", str(data.get("arrived_missed", "—")))
    console.print(t)
    for w in data.get("per_warehouse", []):
        console.print(f"  [dim]{w['warehouse_id']}[/dim] — tickets={w['todays_tickets']} sold={w['todays_sold']} missed={w['arrived_missed']}")


@reports_app.command("stock")
def reports_stock(warehouse_id: Optional[str] = typer.Option(None, help="Warehouse ID filter")):
    """Show stock totals aggregation."""
    params = {}
    if warehouse_id:
        params["warehouse_id"] = warehouse_id
    data = _get("/reports/stock", params=params)
    records = data if isinstance(data, list) else data.get("stock", [])
    if not records:
        console.print("[yellow]No stock data returned.[/yellow]")
        return
    t = _table("SKU / Product", "On Hand", "Available", "Reserved", "Damaged")
    for r in records:
        t.add_row(
            r.get("product_name", r.get("sku", "—")),
            str(r.get("on_hand", "—")),
            str(r.get("available", "—")),
            str(r.get("reserved", "—")),
            str(r.get("damaged", "—")),
        )
    console.print(t)


@reports_app.command("export")
def reports_export(
    report_type: str = typer.Option("arrived", help="Report type: arrived | sold | stock"),
    fmt: str = typer.Option("csv", help="Format: csv | xlsx"),
    date: Optional[str] = typer.Option(None, help="Target date YYYY-MM-DD"),
    out: Optional[Path] = typer.Option(None, help="Output file path (defaults to stdout for csv)"),
):
    """
    Export a report as CSV or XLSX.

    NOTE: The backend /reports/export endpoint is not yet implemented.
    This command fetches the equivalent feed endpoint and renders it locally.
    """
    console.print("[yellow]Note: /reports/export endpoint not yet implemented on server.[/yellow]")
    console.print("[yellow]Fetching equivalent feed endpoint and rendering locally...[/yellow]")

    params: dict = {}
    if date:
        params["date"] = date

    if report_type == "arrived":
        data = _get("/reports/arrived-today", params=params)
        records = data if isinstance(data, list) else data.get("records", [])
        fieldnames = ["ticket_id", "warehouse_id", "tracking_number", "status", "arrived_by", "created_at"]
    elif report_type == "sold":
        data = _get("/reports/sold-today", params=params)
        records = data if isinstance(data, list) else data.get("records", [])
        fieldnames = ["item_id", "barcode", "product_name", "warehouse_id", "order_id", "created_at"]
    else:
        console.print("[red]report_type must be one of: arrived, sold[/red]")
        raise typer.Exit(1)

    if fmt == "csv":
        dest = open(out, "w", newline="") if out else sys.stdout
        writer = csv.DictWriter(dest, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
        if out:
            dest.close()
            console.print(f"[green]Exported {len(records)} rows → {out}[/green]")
    else:
        console.print("[red]xlsx output requires the backend export endpoint (not yet implemented).[/red]")
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# Chat sub-app
# ---------------------------------------------------------------------------

@app.command()
def chat(
    query: str = typer.Argument(..., help="Natural language stock query"),
    warehouse_id: Optional[str] = typer.Option(None, help="Warehouse ID filter"),
):
    """Run a natural language stock query."""
    body: dict = {"query": query}
    if warehouse_id:
        body["warehouse_id"] = warehouse_id
    data = _post("/query", body)
    result = data.get("result", data.get("response", data))
    console.print(result)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app()

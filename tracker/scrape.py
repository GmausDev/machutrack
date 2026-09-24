"""Take one snapshot of the public availability board and append it to data/snapshots.csv.

Loads the page once in headless Chromium (the page is an Angular app, so a
plain HTTP GET returns no data) and reads the rendered text.

Env vars (optional):
  CHROMIUM_PATH        path to a Chromium binary (default: Playwright's own)
  HTTPS_PROXY          proxy to route the browser through
  CHROMIUM_EXTRA_ARGS  extra space-separated Chromium flags
"""
import csv
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright

from tracker.parse import parse

URL = "https://tuboleto.cultura.pe/disponibilidad/llaqta_machupicchu"
LIMA = ZoneInfo("America/Lima")
CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "snapshots.csv"
FIELDS = [
    "captured_utc", "captured_lima", "fecha_visita", "inicio_venta",
    "turnos_disponibles", "turnos_entregados",
    "ruta", "aforo", "vendidos", "disponibles",
]


def fetch_text() -> str:
    launch = {}
    if os.environ.get("CHROMIUM_PATH"):
        launch["executable_path"] = os.environ["CHROMIUM_PATH"]
    if os.environ.get("HTTPS_PROXY"):
        launch["proxy"] = {"server": os.environ["HTTPS_PROXY"]}
    if os.environ.get("CHROMIUM_EXTRA_ARGS"):
        launch["args"] = os.environ["CHROMIUM_EXTRA_ARGS"].split()

    with sync_playwright() as p:
        browser = p.chromium.launch(**launch)
        page = browser.new_page(locale="es-PE")
        page.goto(URL, wait_until="networkidle", timeout=90_000)
        page.get_by_text("DISPONIBLES").first.wait_for(timeout=30_000)
        text = page.inner_text("body")
        browser.close()
    return text


def append(snapshot, now: datetime) -> int:
    new_file = not CSV_PATH.exists()
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        for r in snapshot.rutas:
            w.writerow({
                "captured_utc": now.astimezone(timezone.utc).isoformat(timespec="seconds"),
                "captured_lima": now.astimezone(LIMA).isoformat(timespec="seconds"),
                "fecha_visita": snapshot.fecha_visita,
                "inicio_venta": snapshot.inicio_venta or "",
                "turnos_disponibles": snapshot.turnos_disponibles if snapshot.turnos_disponibles is not None else "",
                "turnos_entregados": snapshot.turnos_entregados if snapshot.turnos_entregados is not None else "",
                "ruta": r.ruta,
                "aforo": r.aforo,
                "vendidos": r.vendidos,
                "disponibles": r.disponibles,
            })
    return len(snapshot.rutas)


def main() -> int:
    snap = parse(fetch_text())
    n = append(snap, datetime.now(timezone.utc))
    print(f"{snap.fecha_visita}: {n} rutas guardadas, turnos entregados={snap.turnos_entregados}")
    for r in snap.rutas:
        print(f"  {r.ruta}: {r.disponibles}/{r.aforo} disponibles")
    return 0


if __name__ == "__main__":
    sys.exit(main())

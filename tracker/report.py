"""Build REPORT.md from data/snapshots.csv.

For each visit date and route: capacity, last seen availability and the Lima
time at which it first hit 0 (sold out). Then a cross-day summary per route,
which is what answers "can I show up without a ticket and get one?".
"""
import csv
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "snapshots.csv"
REPORT_PATH = ROOT / "REPORT.md"


def load(path: Path = CSV_PATH) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def summarize(rows: list[dict]) -> dict:
    """{fecha: {ruta: {...}}, sorted by capture time."""
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by[r["fecha_visita"]][r["ruta"]].append(r)
    out = {}
    for fecha, rutas in sorted(by.items()):
        out[fecha] = {}
        for ruta, snaps in sorted(rutas.items()):
            snaps.sort(key=lambda s: s["captured_utc"])
            sold_out = next((s["captured_lima"] for s in snaps if int(s["disponibles"]) == 0), None)
            last = snaps[-1]
            out[fecha][ruta] = {
                "aforo": int(last["aforo"]),
                "disponibles": int(last["disponibles"]),
                "ultima_captura": last["captured_lima"],
                "agotado_a_las": sold_out,
                "capturas": len(snaps),
            }
    return out


def _hhmm(iso: str | None) -> str:
    return datetime.fromisoformat(iso).strftime("%d/%m %H:%M") if iso else "—"


def _minutes_of_day(iso: str) -> int:
    t = datetime.fromisoformat(iso)
    return t.hour * 60 + t.minute


def render(summary: dict) -> str:
    lines = ["# Machu Picchu – venta presencial (Centro Cultural)", ""]
    if not summary:
        return "\n".join(lines + ["Aún no hay datos."])

    lines += [
        "Horas en hora de Lima. «Agotado a las» = primera captura en la que la ruta llegó a 0.",
        "",
        "## Resumen por ruta",
        "",
        "| Ruta | Días observados | Días agotada | Hora mediana de agotamiento |",
        "|---|---|---|---|",
    ]
    per_route = defaultdict(list)
    for rutas in summary.values():
        for ruta, s in rutas.items():
            per_route[ruta].append(s)
    for ruta, days in sorted(per_route.items()):
        sold = [d["agotado_a_las"] for d in days if d["agotado_a_las"]]
        median = "—"
        if sold:
            m = int(statistics.median(_minutes_of_day(t) for t in sold))
            median = f"{m // 60:02d}:{m % 60:02d}"
        lines.append(f"| {ruta} | {len(days)} | {len(sold)} | {median} |")

    lines += ["", "## Detalle por día de visita", ""]
    for fecha in sorted(summary, reverse=True):
        lines += [
            f"### {fecha}", "",
            "| Ruta | Aforo | Disponibles (última) | Última captura | Agotado a las |",
            "|---|---|---|---|---|",
        ]
        for ruta, s in summary[fecha].items():
            lines.append(
                f"| {ruta} | {s['aforo']} | {s['disponibles']} | {_hhmm(s['ultima_captura'])} | {_hhmm(s['agotado_a_las'])} |"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    REPORT_PATH.write_text(render(summarize(load())), encoding="utf-8")
    print(f"Escrito {REPORT_PATH}")


if __name__ == "__main__":
    main()

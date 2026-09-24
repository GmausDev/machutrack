from pathlib import Path

from tracker.parse import parse
from tracker.report import render, summarize

FIXTURE = Path(__file__).parent / "fixtures" / "page_2026-09-24.txt"


def test_parse_fixture():
    snap = parse(FIXTURE.read_text(encoding="utf-8"))
    assert snap.fecha_visita == "2026-09-25"
    assert snap.inicio_venta == "06:00 AM"
    assert snap.turnos_disponibles == 411
    assert snap.turnos_entregados == 589
    by = {r.ruta: r for r in snap.rutas}
    assert len(by) == 6
    r = by["Ruta 2-A: Clásico Diseñada"]
    assert (r.aforo, r.vendidos, r.disponibles) == (600, 447, 153)


def _row(t, ruta, disp, fecha="2026-09-25"):
    return {"fecha_visita": fecha, "ruta": ruta, "captured_utc": t, "captured_lima": t,
            "aforo": "50", "disponibles": str(disp)}


def test_sold_out_time():
    rows = [
        _row("2026-09-24T09:00:00-05:00", "R", 10),
        _row("2026-09-24T10:00:00-05:00", "R", 0),
        _row("2026-09-24T11:00:00-05:00", "R", 0),
    ]
    s = summarize(rows)["2026-09-25"]["R"]
    assert s["agotado_a_las"] == "2026-09-24T10:00:00-05:00"
    assert "10:00" in render(summarize(rows))

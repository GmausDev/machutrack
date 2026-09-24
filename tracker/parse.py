"""Parse the text of https://tuboleto.cultura.pe/disponibilidad/llaqta_machupicchu.

The page is the public board for in-person sales at the Centro Cultural
(Machu Picchu Pueblo). It shows next-day availability per route plus the
number of queue turns ("turnos") handed out.
"""
import re
from dataclasses import dataclass


@dataclass
class Route:
    ruta: str
    aforo: int
    vendidos: int
    disponibles: int


@dataclass
class Snapshot:
    fecha_visita: str  # YYYY-MM-DD, the day the tickets are for
    inicio_venta: str | None
    turnos_disponibles: int | None
    turnos_entregados: int | None
    rutas: list[Route]


ROUTE_RE = re.compile(
    r"(Ruta [^\n]+?)\s*\n\s*(\d+)\s*\n\s*AFORO\s*\n\s*(\d+)\s*\n\s*VENDIDOS\s*\n\s*(\d+)\s*\n\s*DISPONIBLES",
    re.IGNORECASE,
)


def _int(pattern: str, text: str) -> int | None:
    m = re.search(pattern, text, re.IGNORECASE)
    return int(m.group(1)) if m else None


def parse(text: str) -> Snapshot:
    m = re.search(r"Disponibilidad para el d[ií]a\s*(\d{2})/(\d{2})/(\d{4})", text, re.IGNORECASE)
    if not m:
        raise ValueError("No se encontró la fecha de disponibilidad en la página")
    fecha = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"

    inicio = re.search(r"Inicia:\s*([0-9:]+\s*[AP]M)", text, re.IGNORECASE)
    rutas = [Route(r.strip(), int(a), int(v), int(d)) for r, a, v, d in ROUTE_RE.findall(text)]
    if not rutas:
        raise ValueError("No se encontraron rutas en la página")

    return Snapshot(
        fecha_visita=fecha,
        inicio_venta=inicio.group(1) if inicio else None,
        turnos_disponibles=_int(r"Disponibles:\s*(\d+)", text),
        turnos_entregados=_int(r"Entregados:\s*(\d+)", text),
        rutas=rutas,
    )

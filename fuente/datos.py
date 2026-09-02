"""
Descarga del catalogo historico de sismos del USGS, acotado a España.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

CACHE = Path(__file__).parent.parent / "cache"
CACHE.mkdir(exist_ok=True)

CABECERAS = {
    "User-Agent": "proyecciones-sismos/1.0 (+https://github.com/adrianezd/proyecciones-sismos)",
    "Accept": "application/json, text/plain, */*",
}

USGS = "https://earthquake.usgs.gov/fdsnws/event/1/query"


def _descargar(url: str, clave: str, params: dict | None = None) -> Any:
    fichero = CACHE / f"{clave}.json"
    try:
        r = httpx.get(url, params=params, headers=CABECERAS,
                      timeout=40.0, follow_redirects=True)
        r.raise_for_status()
        datos = r.json()
        fichero.write_text(json.dumps(datos), encoding="utf-8")
        print(f"  descargado  {clave}")
        return datos
    except Exception as e:
        if fichero.exists():
            print(f"  CACHE       {clave}  ({type(e).__name__})")
            return json.loads(fichero.read_text(encoding="utf-8"))
        print(f"  FALLO       {clave}  ({e})")
        return None


def sismos(desde: int = 1990, magnitud_min: float = 3.0) -> list[dict]:
    """Sismos del entorno peninsular, Baleares y Canarias.

    Para magnitudes pequeñas el catalogo del IGN es mas completo en
    territorio español; para las medias y altas, que es lo que interesa
    aqui, el del USGS sirve y tiene una API mucho mas comoda.
    """
    datos = _descargar(USGS, f"sismos-{desde}-{magnitud_min}", {
        "format": "geojson",
        "starttime": f"{desde}-01-01",
        "minmagnitude": magnitud_min,
        "minlatitude": 27.0, "maxlatitude": 44.5,
        "minlongitude": -19.0, "maxlongitude": 5.0,
        "orderby": "time", "limit": 20000,
    })
    if not isinstance(datos, dict):
        return []

    salida = []
    for f in datos.get("features", []):
        p = f.get("properties") or {}
        g = (f.get("geometry") or {}).get("coordinates") or [None, None, None]
        if not isinstance(p.get("mag"), (int, float)):
            continue
        salida.append({
            "mag": round(float(p["mag"]), 1),
            "lugar": p.get("place") or "",
            "tiempo": p.get("time"),
            "profundidad": g[2] if len(g) > 2 else None,
        })
    return salida

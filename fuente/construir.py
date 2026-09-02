"""
Generador de esta pagina: cada cuanto tiembla en España.

    python -m fuente.construir
"""

from __future__ import annotations

import datetime as dt
import json
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import calculo, datos
from .enlaces import HUB, MENU

AQUI = Path(__file__).parent
PROYECTO = AQUI.parent
SALIDA = PROYECTO / "docs"

BASE_URL = "https://adrianezd.github.io/proyecciones-sismos"

entorno = Environment(
    loader=FileSystemLoader(AQUI / "plantillas"),
    autoescape=select_autoescape(["html"]),
)

HOY = dt.date.today().isoformat()


def json_seguro(obj) -> str:
    texto = json.dumps(obj, ensure_ascii=False)
    return (texto
            .replace("<", "\\u003c")
            .replace(">", "\\u003e")
            .replace("&", "\\u0026")
            .replace(" ", "\\u2028")
            .replace(" ", "\\u2029"))


def escribir(plantilla: str, **contexto) -> None:
    destino = SALIDA / "index.html"
    destino.parent.mkdir(parents=True, exist_ok=True)

    contexto.setdefault("raiz", "./")
    contexto.setdefault("menu", MENU)
    contexto.setdefault("hub", HUB)
    contexto.setdefault("base_url", BASE_URL)
    contexto.setdefault("ruta", "")
    contexto.setdefault("generado", HOY)

    destino.write_text(entorno.get_template(plantilla).render(**contexto), encoding="utf-8")
    print("  escrito     index.html")


def main() -> None:
    print("Construyendo: sismos\n")

    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    SALIDA.mkdir(parents=True)
    shutil.copytree(PROYECTO / "estatico", SALIDA / "estatico")

    desde = 1990
    eventos = datos.sismos(desde, 3.0)
    if len(eventos) < 20:
        print("  SALTADA     sismos (catalogo vacio)")
        (SALIDA / ".nojekyll").write_text("", encoding="utf-8")
        return

    anios = max(1.0, dt.date.today().year - desde)
    magnitudes = [e["mag"] for e in eventos]
    por_anio = calculo.sismos_por_anio(eventos)

    escribir(
        "sismos.html",
        acento="sismos",
        titulo="Cada cuanto tiembla en España",
        descripcion=f"{len(eventos)} terremotos de magnitud 3 o mas registrados en España "
                    f"desde {desde}, y cada cuantos años se repite cada magnitud.",
        desde=desde,
        total=len(eventos),
        anios_catalogo=round(anios),
        por_anio_media=round(len(eventos) / anios, 1),
        por_anio=round(len(eventos) / anios, 1),
        retornos=calculo.periodos_retorno(magnitudes, anios),
        mayores=sorted(eventos, key=lambda e: -e["mag"])[:10],
        datos_json=json_seguro({"por_anio": por_anio}),
    )

    (SALIDA / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8"
    )
    (SALIDA / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'\n  <url><loc>{BASE_URL}/</loc><lastmod>{HOY}</lastmod></url>\n</urlset>\n',
        encoding="utf-8",
    )
    (SALIDA / ".nojekyll").write_text("", encoding="utf-8")

    print("\nListo.")


if __name__ == "__main__":
    main()

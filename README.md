# Proyecciones: Sismos en España

Cada cuánto tiembla en España, según el catálogo histórico desde 1990.

Sitio en vivo: https://adrianezd.github.io/proyecciones-sismos/

Parte de [Proyecciones](https://adrianezd.github.io/proyecciones/), once páginas de datos públicos, cada una
en su propio repositorio y su propio GitHub Pages.

## Fuente de datos

**USGS**, catálogo sísmico acotado a la Península, Baleares y Canarias.

## Cómo funciona

No hay servidor. Una GitHub Action (dos veces al día) descarga la fuente, calcula
lo que haga falta y escribe HTML plano con los datos ya incrustados en
`docs/`. GitHub Pages sirve esa carpeta directamente.

Si la fuente falla y no hay copia en `cache/` (que se versiona en el
repo), la página no se genera: nunca se rellena un hueco con datos
inventados.

## Arrancar en local

```bash
pip install -r requirements.txt
python -m fuente.construir
python -m http.server 8000 --directory docs
```

## Publicar

1. Sube el repo a GitHub.
2. Settings → Pages → Source: **GitHub Actions**.
3. Actions → *Construir y publicar* → **Run workflow**.

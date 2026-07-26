#!/usr/bin/env python3
"""Convierte links cortos de Google Maps a coordenadas (lat, lon)."""
import json
import re
import sys
from html import unescape
from urllib.parse import unquote

import requests

# UA de navegador + cookie de consentimiento para saltar la pagina de consent de Google.
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
CONSENT_COOKIE = "CAISHAgBEhJnd3NfMjAyMzA4MTAtMF9SQzIaAmVuIAEaBgiA_LyrBg"


_SESSION = None


def _session():
    """Sesion persistente (reusa conexiones TLS con google.com entre consultas)."""
    global _SESSION
    if _SESSION is None:
        _SESSION = requests.Session()
        _SESSION.headers.update(HEADERS)
        _SESSION.cookies.set("SOCS", CONSENT_COOKIE, domain=".google.com")
    return _SESSION


def _coords_from_url(url: str):
    """Coords directas en la URL (pines de coordenadas). None si no hay."""
    url = unquote(url)
    for pat in (
        r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)",
        r"@(-?\d+\.\d+),(-?\d+\.\d+)",
        r"[?&](?:q|ll)=(-?\d+\.\d+),(-?\d+\.\d+)",
    ):
        m = re.search(pat, url)
        if m:
            return float(m.group(1)), float(m.group(2))
    return None


def _place_href(response):
    """Lee la respuesta en streaming y devuelve el href de /maps/preview/place.

    El enlace esta al inicio del <head>, asi que cortamos en cuanto aparece
    (evita descargar los ~190 KB completos de la pagina del lugar)."""
    pat = re.compile(r'href="(/maps/preview/place\?[^"]+)"')
    buf = ""
    for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
        buf += chunk
        m = pat.search(buf)
        if m:
            response.close()
            return m.group(1)
        if len(buf) > 300_000:
            break
    return None


def _coords_from_place(session, response):
    """Coords de un lugar (negocio/direccion) via el endpoint interno de Maps."""
    href = _place_href(response)
    if not href:
        return None
    body = session.get("https://www.google.com" + unescape(href), timeout=15).text
    data = json.loads(body[body.find("["):])
    try:
        _, _, lat, lon = data[6][9]  # [null, null, lat, lon]
        return float(lat), float(lon)
    except (IndexError, TypeError, ValueError):
        return None


def short_to_coords(short_url: str):
    """Devuelve (lat, lon) del link corto/largo de Google Maps, o None."""
    session = _session()
    r = session.get(short_url, allow_redirects=True, timeout=15, stream=True)
    coords = _coords_from_url(r.url)
    if coords:
        r.close()
        return coords
    return _coords_from_place(session, r)


def main():
    if len(sys.argv) < 2:
        print("Uso: python maps_coords.py <link_de_google_maps> [...]")
        sys.exit(1)
    for link in sys.argv[1:]:
        coords = short_to_coords(link)
        if coords:
            print(f"{coords[0]}, {coords[1]}")
        else:
            print(f"No se encontraron coordenadas en: {link}", file=sys.stderr)


if __name__ == "__main__":
    main()

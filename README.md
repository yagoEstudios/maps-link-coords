# maps-link-coords

Convierte links cortos de Google Maps (`maps.app.goo.gl`, `goo.gl/maps`) a coordenadas lat/lon.

**Web en vivo:** https://yagrok.pythonanywhere.com

## Uso

```bash
python maps_coords.py https://maps.app.goo.gl/xxxxxxxx
# -> 40.4169473, -3.7035285
```

Acepta varios links a la vez. Requiere `requests` (`pip install requests`).

## Cómo funciona

Sigue la redirección del link corto y extrae las coordenadas de la URL final
(patrones `!3d..!4d..`, `@lat,lon`, o `q=lat,lon`).

# Copia el contenido de este archivo en el WSGI file que crea PythonAnywhere
# (Web tab -> "WSGI configuration file"). Cambia TU_USUARIO por tu usuario.
import sys

path = "/home/TU_USUARIO/maps-link-coords/web"
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application  # noqa: E402,F401

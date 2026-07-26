import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from maps_coords import short_to_coords  # noqa: E402

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/coords", methods=["POST"])
def coords():
    link = (request.form.get("url") or "").strip()
    if not link:
        return jsonify(error="Pega un link de Google Maps"), 400
    try:
        result = short_to_coords(link)
    except Exception as e:
        return jsonify(error=f"Error resolviendo el link: {e}"), 502
    if not result:
        return jsonify(error="No se encontraron coordenadas en ese link"), 404
    lat, lon = result
    return jsonify(lat=lat, lon=lon)


if __name__ == "__main__":
    app.run(debug=True, port=5000)

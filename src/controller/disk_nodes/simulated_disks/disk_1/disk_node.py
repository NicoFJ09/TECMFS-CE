#!/usr/bin/env python3
import os
import sys
import xml.etree.ElementTree as ET
from flask import Flask, request, abort

# -----------------------------------
# 1) Cargar y parsear XML de config
# -----------------------------------
if len(sys.argv) != 2:
    print("Uso: disk_node.py <ruta_a_disk_node_config.xml>")
    sys.exit(1)

cfg_path = sys.argv[1]
tree = ET.parse(cfg_path)
root = tree.getroot()

# Datos del Controller (aunque aquí solo usamos el puerto)
ctrl_ip   = root.find("Controller/IP").text
ctrl_port = int(root.find("Controller/Port").text)

# Datos del Storage
storage_path = root.find("Storage/Path").text
# Si la ruta es relativa, convertirla relativa al XML
if not os.path.isabs(storage_path):
    base = os.path.dirname(cfg_path)
    storage_path = os.path.abspath(os.path.join(base, storage_path))

disk_size = int(root.find("Storage/DiskSize").text)
blk_size  = int(root.find("Storage/BlockSize").text)
n_blocks  = disk_size // blk_size

# -----------------------------------
# 2) Inicializar (o reinicializar) disk.img
# -----------------------------------
os.makedirs(storage_path, exist_ok=True)
disk_file = os.path.join(storage_path, "disk.img")
# Siempre (re)crear y trun­car a ceros
with open(disk_file, "wb") as f:
    f.truncate(disk_size)


# -----------------------------------
# 3) Arrancar Flask
# -----------------------------------
app = Flask(__name__)

def block_offset(idx: int) -> int:
    """Devuelve el offset byte en disk.img para el bloque idx."""
    if idx < 0 or idx >= n_blocks:
        abort(404, f"Bloque {idx} fuera de rango")
    return idx * blk_size

@app.route("/block", methods=["GET"])
def read_block():
    """GET /block?idx=<i>  → devuelve el bloque i (4096B por defecto)."""
    try:
        idx = int(request.args.get("idx", "-1"))
    except ValueError:
        abort(400, "Índice inválido")
    ofs = block_offset(idx)
    with open(disk_file, "rb") as f:
        f.seek(ofs)
        data = f.read(blk_size)
    return data, 200, {"Content-Type": "application/octet-stream"}

@app.route("/block", methods=["POST"])
def write_block():
    """POST /block?idx=<i> (body binario) → escribe exactamente blk_size bytes."""
    try:
        idx = int(request.args.get("idx", "-1"))
    except ValueError:
        abort(400, "Índice inválido")
    body = request.get_data()
    if len(body) != blk_size:
        abort(400, f"Se esperaban {blk_size} bytes, llegaron {len(body)}")
    ofs = block_offset(idx)
    with open(disk_file, "r+b") as f:
        f.seek(ofs)
        f.write(body)
    return ("", 204)

if __name__ == "__main__":
    # Arranca en el puerto indicado por el XML
    app.run(host="0.0.0.0", port=ctrl_port)

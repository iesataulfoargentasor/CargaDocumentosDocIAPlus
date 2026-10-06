"""Ejecutar con el servidor detenido. Nunca recibe contraseñas por argumentos."""
import argparse
import getpass
import json
import os
import re
from pathlib import Path
from werkzeug.security import generate_password_hash

parser = argparse.ArgumentParser(description="Crear una cuenta autorizada del piloto")
parser.add_argument("usuario")
args = parser.parse_args()
if not re.fullmatch(r"[a-zA-Z0-9_.-]{3,40}", args.usuario):
    parser.error("Usuario: 3–40 letras, números, punto, guion o guion bajo.")
path = Path(__file__).resolve().parent.parent / "instance/users.json"
users = json.loads(path.read_text()) if path.exists() else {}
if args.usuario in users:
    parser.error("La cuenta ya existe; no se sobrescribirá.")
password = getpass.getpass("Contraseña (mínimo 12 caracteres): ")
if len(password) < 12 or len(password) > 256 or password != getpass.getpass("Repite la contraseña: "):
    parser.error("Longitud no válida o contraseñas distintas.")
users[args.usuario] = {"password_hash": generate_password_hash(password), "active": True, "permissions": ["read", "upload"]}
path.parent.mkdir(exist_ok=True)
temp = path.with_suffix(".tmp")
fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, "w") as output:
    json.dump(users, output, indent=2)
os.replace(temp, path)
print("Cuenta creada. No se han enviado datos a AWS.")

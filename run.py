"""Servidor local de un solo proceso (necesario para el bloqueo de altas)."""
import os
from waitress import serve
from app import create_app

if __name__ == "__main__":
    app = create_app()
    if not app.config["S3_BUCKET"]:
        raise SystemExit("Configura S3_BUCKET en .env antes de iniciar.")
    print("Gestor de programaciones: http://"+os.getenv("HOST", "127.0.0.1")+":"+os.getenv("PORT", "5000"))
    serve(app, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")), threads=4,
          max_request_body_size=app.config["MAX_CONTENT_LENGTH"])

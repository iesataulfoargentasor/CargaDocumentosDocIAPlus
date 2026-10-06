import json
import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template
from app.models.user import UserStore
from app.repositories.s3_repository import S3Repository, StorageError, NotFound
from app.services.document_service import DocumentService
from app.security import LoginLimiter, csrf_token, protect_request

ROOT = Path(__file__).resolve().parent.parent

def create_app(test_config=None, repository=None):
    load_dotenv(ROOT / ".env")
    app = Flask(__name__, instance_path=str(ROOT / "instance"))
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY"), CENTRO=os.getenv("CENTRO", "IES Ataúlfo Argenta"),
        S3_BUCKET=os.getenv("S3_BUCKET", ""), S3_PREFIX=os.getenv("S3_PREFIX", "programaciones").strip("/"),
        AWS_REGION=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        MAX_FILE_BYTES=int(os.getenv("MAX_FILE_MB", "20"))*1024*1024,
        SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE", "false").lower() == "true",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
        USERS_FILE=str(ROOT / "instance/users.json"),
        CATALOG=json.loads((ROOT / "config/catalogo.json").read_text(encoding="utf-8")),
    )
    if test_config:
        app.config.update(test_config)
    if not app.config["SECRET_KEY"] or len(app.config["SECRET_KEY"]) < 32 or app.config["SECRET_KEY"].startswith("REEMPLAZAR"):
        raise RuntimeError("Configura una SECRET_KEY aleatoria de al menos 32 caracteres en .env.")
    if not app.config["S3_PREFIX"]:
        raise RuntimeError("S3_PREFIX no puede estar vacío.")
    app.config["MAX_CONTENT_LENGTH"] = app.config["MAX_FILE_BYTES"] + 1024*1024
    app.config["MAX_FORM_MEMORY_SIZE"] = 128*1024
    app.config["MAX_FORM_PARTS"] = 30
    app.extensions["users"] = UserStore(app.config["USERS_FILE"])
    app.extensions["documents"] = DocumentService(repository if repository is not None else S3Repository(
        app.config["S3_BUCKET"], app.config["S3_PREFIX"], app.config["AWS_REGION"]))
    app.extensions["login_limiter"] = LoginLimiter()
    app.before_request(protect_request)
    app.jinja_env.globals["csrf_token"] = csrf_token
    @app.context_processor
    def context():
        return {"catalog": app.config["CATALOG"], "center": app.config["CENTRO"],
                "max_file_mb": app.config["MAX_FILE_BYTES"]//(1024*1024)}
    from app.controllers.auth_controller import auth
    from app.controllers.document_controller import documents
    app.register_blueprint(auth)
    app.register_blueprint(documents)

    @app.after_request
    def headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.errorhandler(StorageError)
    def storage_error(error):
        return render_template("error.html", title="No se pudo completar la operación", message=str(error)), 503
    @app.errorhandler(NotFound)
    def not_found(error):
        return render_template("error.html", title="Documento no encontrado", message="Revisa el enlace o vuelve al catálogo."), 404
    for code, title, message in [(400,"Formulario no válido","Recarga la página y vuelve a intentarlo."),
        (403,"Acceso denegado","Tu cuenta no tiene permiso para esta operación."),
        (404,"Página no encontrada","Vuelve al catálogo para continuar."),
        (413,"Carga demasiado grande","El archivo o la petición supera el límite configurado."),
        (500,"Error interno","No se ha confirmado la operación. Consulta el catálogo antes de repetirla.")]:
        def handler(error, code=code, title=title, message=message):
            return render_template("error.html", title=title, message=message), code
        app.register_error_handler(code, handler)
    return app

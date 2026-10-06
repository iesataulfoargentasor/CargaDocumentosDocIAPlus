import io
from flask import Blueprint, current_app, flash, g, redirect, render_template, request, send_file, url_for
from app.security import permission_required
from app.services.document_service import Duplicate, PossibleRevision
from app.services.validation import ValidationError, validate_file, validate_metadata

documents = Blueprint("documents", __name__)

def repo():
    return current_app.extensions["documents"].repository

@documents.get("/")
@permission_required("read")
def catalog():
    records = repo().list_all()
    filters = {k: request.args.get(k, "").strip() for k in ("q", "modulo", "curso_academico", "estado_declarado")}
    selected = [r for r in records if all(not v or (v.casefold() in r["titulo"].casefold() if k == "q" else r.get(k) == v) for k, v in filters.items())]
    return render_template("documents/catalog.html", records=selected, filters=filters)

@documents.route("/programaciones/nueva", methods=["GET", "POST"])
@permission_required("upload")
def upload():
    errors, candidates = {}, []
    if request.method == "POST":
        try:
            metadata = validate_metadata(request.form, current_app.config["CATALOG"], current_app.config["CENTRO"])
            file = validate_file(request.files.get("archivo"), current_app.config["MAX_FILE_BYTES"])
            record = current_app.extensions["documents"].create(metadata, file, session_username(), request.form)
            flash("Programación guardada correctamente. Esto no implica aprobación oficial ni publicación en un RAG.", "success")
            return redirect(url_for("documents.detail", document_id=record["id"]))
        except ValidationError as exc:
            errors = exc.errors
        except Duplicate as exc:
            return render_template("documents/duplicate.html", record=exc.record, mismatch=exc.mismatch), 409
        except PossibleRevision as exc:
            candidates = exc.candidates
            errors["relacion"] = "Ya existe documentación del mismo módulo y curso. Indica la relación y vuelve a seleccionar el archivo para confirmar."
    return render_template("documents/upload.html", form=request.form, errors=errors, candidates=candidates), (422 if errors else 200)

def session_username():
    from flask import session
    return session["username"]

@documents.get("/programaciones/<document_id>")
@permission_required("read")
def detail(document_id):
    return render_template("documents/detail.html", record=repo().get(document_id))

@documents.get("/programaciones/<document_id>/descargar")
@permission_required("read")
def download(document_id):
    record = repo().get(document_id)
    content = repo().download(record, current_app.config["MAX_FILE_BYTES"])
    return send_file(io.BytesIO(content), as_attachment=True, download_name=record["archivo"]["nombre_original"],
                     mimetype=record["archivo"]["tipo_mime"], max_age=0)

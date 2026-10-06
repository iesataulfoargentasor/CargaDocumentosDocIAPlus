"""Validación del formulario y lectura básica de formatos permitidos."""
import hashlib
import io
import zipfile
from pathlib import PurePosixPath
from pypdf import PdfReader
from docx import Document
from app.models.document import ValidatedFile

class ValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__("Comprueba los campos indicados.")

def validate_metadata(form, catalog, center):
    fields = ("titulo", "ensenanza", "modulo", "curso_academico", "estado_declarado", "procedencia", "observaciones")
    result = {k: form.get(k, "").strip() for k in fields}
    errors = {}
    if not 5 <= len(result["titulo"]) <= 150:
        errors["titulo"] = "Escribe un título de entre 5 y 150 caracteres."
    teaching = catalog["ensenanzas"].get(result["ensenanza"])
    if not teaching:
        errors["ensenanza"] = "Selecciona una enseñanza del catálogo."
    if not teaching or result["modulo"] not in teaching["modulos"]:
        errors["modulo"] = "El módulo debe pertenecer a la enseñanza seleccionada."
    if result["curso_academico"] not in catalog["cursos"]:
        errors["curso_academico"] = "Selecciona un curso permitido."
    if result["estado_declarado"] not in ("borrador", "final"):
        errors["estado_declarado"] = "Indica si es borrador o documento final."
    if not 3 <= len(result["procedencia"]) <= 200:
        errors["procedencia"] = "Indica la procedencia (3–200 caracteres)."
    if len(result["observaciones"]) > 2000:
        errors["observaciones"] = "Máximo 2000 caracteres."
    if errors:
        raise ValidationError(errors)
    return {"centro": center, **result}

def validate_file(storage, max_bytes):
    if not storage or not storage.filename:
        raise ValidationError({"archivo": "Selecciona un archivo."})
    filename = PurePosixPath(storage.filename.replace("\\", "/")).name
    if len(filename) > 200 or any(ord(c) < 32 for c in filename):
        raise ValidationError({"archivo": "El nombre del archivo no es válido (máximo 200 caracteres)."})
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ("pdf", "docx", "txt"):
        raise ValidationError({"archivo": "Solo se permiten PDF, DOCX y TXT."})
    content = storage.stream.read(max_bytes + 1)
    if not content:
        raise ValidationError({"archivo": "El archivo está vacío."})
    if len(content) > max_bytes:
        raise ValidationError({"archivo": "El archivo supera el tamaño máximo permitido."})
    try:
        if extension == "pdf":
            if not content.startswith(b"%PDF-"):
                raise ValueError()
            pdf = PdfReader(io.BytesIO(content), strict=True)
            if pdf.is_encrypted:
                raise ValidationError({"archivo": "No se admiten PDF cifrados o con contraseña."})
            if not len(pdf.pages):
                raise ValueError()
            for page in pdf.pages:
                # Recorre la estructura; no exige texto ni realiza OCR.
                _ = page.mediabox
            mime = "application/pdf"
        elif extension == "docx":
            if not zipfile.is_zipfile(io.BytesIO(content)):
                raise ValueError()
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                infos = archive.infolist()
                if len(infos) > 2000 or sum(i.file_size for i in infos) > 80 * 1024 * 1024:
                    raise ValidationError({"archivo": "El DOCX descomprimido supera los límites del piloto."})
                names = archive.namelist()
                if "word/document.xml" not in names or "[Content_Types].xml" not in names:
                    raise ValueError()
                if any("vbaproject" in n.lower() or n.startswith("word/embeddings/") for n in names):
                    raise ValidationError({"archivo": "No se admiten macros ni objetos incrustados."})
                if b"macroEnabled" in archive.read("[Content_Types].xml") or archive.testzip():
                    raise ValueError()
            Document(io.BytesIO(content))
            mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            text = content.decode("utf-8-sig")
            if not text.strip() or any(ord(c) < 32 and c not in "\n\r\t" for c in text):
                raise ValueError()
            mime = "text/plain"
    except ValidationError:
        raise
    except Exception as exc:
        raise ValidationError({"archivo": "El contenido no corresponde al formato, es ilegible o está corrupto. Los TXT deben estar en UTF-8."}) from exc
    return ValidatedFile(content, filename, extension, mime, hashlib.sha256(content).hexdigest())

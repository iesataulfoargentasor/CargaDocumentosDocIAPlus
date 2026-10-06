"""Reglas de negocio independientes de Flask y S3."""
from threading import Lock
from app.models.document import identity, new_document
from app.services.validation import ValidationError

class Duplicate(Exception):
    def __init__(self, record, mismatch):
        self.record, self.mismatch = record, mismatch

class PossibleRevision(Exception):
    def __init__(self, candidates):
        self.candidates = candidates

class DocumentService:
    def __init__(self, repository):
        self.repository = repository
        self.upload_lock = Lock()  # Una instancia / un proceso; véase README.

    def create(self, metadata, upload, username, form):
        with self.upload_lock:
            records = self.repository.list_all()
            for existing in records:
                if existing["archivo"]["sha256"] == upload.sha256:
                    raise Duplicate(existing, identity(existing) != identity(metadata))
            candidates = [r for r in records if identity(r) == identity(metadata)]
            relation = None
            if candidates:
                target = form.get("relacion_id", "")
                kind = form.get("relacion_tipo", "")
                reason = form.get("relacion_motivo", "").strip()
                if not target or not kind:
                    raise PossibleRevision(candidates)
                if target not in {r["id"] for r in candidates} or kind not in ("revision", "complemento") or not 5 <= len(reason) <= 500:
                    raise ValidationError({"relacion": "Selecciona un documento coincidente, un tipo de relación y un motivo de 5–500 caracteres."})
                relation = {"tipo": kind, "documento_id": target, "motivo": reason}
            record = new_document(metadata, upload, username, self.repository.prefix, relation)
            self.repository.save(record, upload.content)
            return record

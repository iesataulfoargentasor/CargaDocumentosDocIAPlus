"""Cuentas del piloto guardadas en configuración local, con hashes scrypt."""
import json
from pathlib import Path
from werkzeug.security import check_password_hash, generate_password_hash

DUMMY_HASH = generate_password_hash("dummy-password-never-used")

class UserStore:
    def __init__(self, path):
        self.path = Path(path)

    def all(self):
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def get(self, username):
        user = self.all().get(username)
        return user if user and user.get("active") else None

    def authenticate(self, username, password):
        user = self.get(username)
        valid = check_password_hash(user["password_hash"] if user else DUMMY_HASH, password)
        return user if user and valid else None

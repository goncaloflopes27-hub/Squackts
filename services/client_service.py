from __future__ import annotations

import db
from utils import nif_valid, simple_email_valid


class ClientService:
    def __init__(self, repo, log_repo):
        self.repo = repo
        self.log_repo = log_repo

    def list_clients(self):
        with db.connect() as conn:
            return [dict(r) for r in self.repo.list_all(conn)]

    def create_client(self, payload: dict) -> str:
        if not payload.get("nome"):
            raise ValueError("Nome obrigatório")
        if not simple_email_valid(payload.get("email", "")):
            raise ValueError("Email inválido")
        if not nif_valid(payload.get("nif", "")):
            raise ValueError("NIF deve ter 9 dígitos")
        with db.transaction() as conn:
            cid = self.repo.create(conn, payload)
            self.log_repo.add(conn, "client_created", f"client={cid}")
            return cid

from werkzeug.security import check_password_hash, generate_password_hash

from src.models.db import get_db


def get_all():
    db = get_db()
    rows = db.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios").fetchall()
    return [dict(row) for row in rows]


def get_by_id(usuario_id):
    db = get_db()
    row = db.execute(
        "SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()
    return dict(row) if row else None


def get_by_email(email):
    db = get_db()
    row = db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    return dict(row) if row else None


def create(nome, email, senha, tipo="cliente"):
    db = get_db()
    senha_hash = generate_password_hash(senha)
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    db.commit()
    return cursor.lastrowid


def authenticate(email, senha):
    """Substitui a comparação em texto puro da versão original por hash real
    (playbook #4 — corrige o finding CRITICAL de senha em texto puro)."""
    usuario = get_by_email(email)
    if usuario and check_password_hash(usuario["senha_hash"], senha):
        return usuario
    return None

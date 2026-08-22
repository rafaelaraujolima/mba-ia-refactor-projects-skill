from flask import jsonify

from src.models.db import get_db


def index():
    return jsonify(
        {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "1.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }
    )


def health_check():
    db = get_db()
    produtos = db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
    usuarios = db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
    pedidos = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]

    # Não inclui mais secret_key/debug na resposta (corrige o finding CRITICAL de
    # segredo vazado via API e o finding MEDIUM de config de debug exposta).
    return (
        jsonify(
            {
                "status": "ok",
                "database": "connected",
                "counts": {"produtos": produtos, "usuarios": usuarios, "pedidos": pedidos},
                "versao": "1.0.0",
            }
        ),
        200,
    )


def reset_database():
    """Protegido por auth_controller.require_auth(role="admin") no registro de rotas —
    corrige o finding HIGH de endpoint destrutivo sem autenticação."""
    db = get_db()
    db.execute("DELETE FROM itens_pedido")
    db.execute("DELETE FROM pedidos")
    db.execute("DELETE FROM produtos")
    db.execute("DELETE FROM usuarios")
    db.commit()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200

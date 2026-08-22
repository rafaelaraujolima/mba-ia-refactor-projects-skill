import logging
from functools import wraps

import jwt
from flask import jsonify, request

from src.config import settings
from src.models import usuario_model

logger = logging.getLogger(__name__)


def issue_token(usuario):
    payload = {"sub": usuario["id"], "role": usuario["tipo"]}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def login():
    dados = request.get_json()
    email = dados.get("email", "") if dados else ""
    senha = dados.get("senha", "") if dados else ""

    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400

    usuario = usuario_model.authenticate(email, senha)
    if not usuario:
        logger.info("Login falhou: %s", email)
        return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401

    token = issue_token(usuario)
    logger.info("Login bem-sucedido: %s", email)
    return (
        jsonify(
            {
                "dados": {
                    "id": usuario["id"],
                    "nome": usuario["nome"],
                    "email": usuario["email"],
                    "tipo": usuario["tipo"],
                },
                "token": token,
                "sucesso": True,
                "mensagem": "Login OK",
            }
        ),
        200,
    )


def require_auth(role=None):
    """Guard de autenticação real via JWT, usado para proteger endpoints sensíveis
    (playbook #6 — corrige o finding HIGH de endpoint administrativo sem autenticação).
    Substitui o "fake-jwt-token" da versão original, que nunca era validado em lugar nenhum."""

    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            token = auth_header[7:] if auth_header.startswith("Bearer ") else auth_header
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            except jwt.InvalidTokenError:
                return jsonify({"erro": "Não autorizado", "sucesso": False}), 401
            if role and payload.get("role") != role:
                return jsonify({"erro": "Acesso negado", "sucesso": False}), 403
            return view(*args, **kwargs)

        return wrapper

    return decorator

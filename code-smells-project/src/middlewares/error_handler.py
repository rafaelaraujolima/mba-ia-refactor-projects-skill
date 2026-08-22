import logging

from flask import jsonify

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Erro de negócio com status HTTP explícito, para ser levantado pelos controllers
    em vez de cada um montar sua própria resposta de erro (playbook #12 — tratamento de
    erro centralizado, parte da estrutura MVC alvo)."""

    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(e):
        return jsonify({"erro": e.message, "sucesso": False}), e.status_code

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        logger.exception("Erro não tratado")
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500

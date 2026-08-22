import logging

from flask import jsonify

logger = logging.getLogger(__name__)


class AppError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(e):
        return jsonify({'error': e.message}), e.status_code

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({'error': 'Recurso não encontrado'}), 404

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        logger.exception('Unhandled error')
        return jsonify({'error': 'Erro interno'}), 500

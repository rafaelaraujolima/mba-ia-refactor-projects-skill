from functools import wraps

import jwt
from flask import g, jsonify, request

from config import settings
from middlewares.error_handler import AppError
from models.user import User


def issue_token(user):
    payload = {'sub': user.id, 'role': user.role}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def _decode_token(token):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.InvalidTokenError:
        return None


def require_auth(role=None):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Não autorizado'}), 401

            token = auth_header[len('Bearer '):]
            payload = _decode_token(token)
            if not payload:
                return jsonify({'error': 'Não autorizado'}), 401

            user = User.query.get(payload.get('sub'))
            if not user or not user.active:
                return jsonify({'error': 'Não autorizado'}), 401

            if role and user.role != role:
                return jsonify({'error': 'Acesso negado'}), 403

            g.current_user = user
            return view(*args, **kwargs)

        return wrapper

    return decorator


def authenticate(email, password):
    if not email or not password:
        raise AppError('Email e senha são obrigatórios', 400)

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise AppError('Credenciais inválidas', 401)

    if not user.active:
        raise AppError('Usuário inativo', 403)

    return {
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': issue_token(user),
    }

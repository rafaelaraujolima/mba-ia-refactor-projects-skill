from flask import Blueprint, g, jsonify, request

from controllers import auth_controller, user_controller
from controllers.auth_controller import require_auth

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['GET'])
def get_users():
    return jsonify(user_controller.list_users()), 200


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return jsonify(user_controller.get_user(user_id)), 200


@user_bp.route('/users', methods=['POST'])
def create_user():
    user = user_controller.create_user(request.get_json(silent=True))
    return jsonify(user), 201


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@require_auth()
def update_user(user_id):
    user = user_controller.update_user(
        user_id, request.get_json(silent=True), acting_user=g.current_user
    )
    return jsonify(user), 200


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_auth(role='admin')
def delete_user(user_id):
    result = user_controller.delete_user(user_id)
    return jsonify(result), 200


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    return jsonify(user_controller.get_user_tasks(user_id)), 200


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    result = auth_controller.authenticate(data.get('email'), data.get('password'))
    return jsonify(result), 200

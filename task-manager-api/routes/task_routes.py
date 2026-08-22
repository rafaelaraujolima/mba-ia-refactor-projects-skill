from flask import Blueprint, jsonify, request

from controllers import task_controller
from controllers.auth_controller import require_auth

task_bp = Blueprint('tasks', __name__)


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(task_controller.list_tasks()), 200


@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    result = task_controller.search_tasks(
        query=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=request.args.get('priority', ''),
        user_id=request.args.get('user_id', ''),
    )
    return jsonify(result), 200


@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    return jsonify(task_controller.get_task_stats()), 200


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    return jsonify(task_controller.get_task(task_id)), 200


@task_bp.route('/tasks', methods=['POST'])
@require_auth()
def create_task():
    task = task_controller.create_task(request.get_json(silent=True))
    return jsonify(task), 201


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@require_auth()
def update_task(task_id):
    task = task_controller.update_task(task_id, request.get_json(silent=True))
    return jsonify(task), 200


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@require_auth()
def delete_task(task_id):
    result = task_controller.delete_task(task_id)
    return jsonify(result), 200

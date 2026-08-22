from flask import Blueprint, jsonify, request

from controllers import report_controller
from controllers.auth_controller import require_auth

report_bp = Blueprint('reports', __name__)


@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    return jsonify(report_controller.summary_report()), 200


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    return jsonify(report_controller.user_report(user_id)), 200


@report_bp.route('/categories', methods=['GET'])
def get_categories():
    return jsonify(report_controller.list_categories()), 200


@report_bp.route('/categories', methods=['POST'])
@require_auth()
def create_category():
    category = report_controller.create_category(request.get_json(silent=True))
    return jsonify(category), 201


@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
@require_auth()
def update_category(cat_id):
    category = report_controller.update_category(cat_id, request.get_json(silent=True))
    return jsonify(category), 200


@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
@require_auth(role='admin')
def delete_category(cat_id):
    result = report_controller.delete_category(cat_id)
    return jsonify(result), 200

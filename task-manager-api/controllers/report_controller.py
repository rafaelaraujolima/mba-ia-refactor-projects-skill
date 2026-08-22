from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import joinedload

from database import db
from middlewares.error_handler import AppError
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import DEFAULT_COLOR, calculate_percentage


def summary_report():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()

    priority_counts = {
        p: Task.query.filter_by(priority=p).count() for p in (1, 2, 3, 4, 5)
    }

    all_tasks = Task.query.all()
    overdue_list = [
        {
            'id': t.id,
            'title': t.title,
            'due_date': str(t.due_date),
            'days_overdue': (datetime.now(timezone.utc) - t.due_date_aware).days,
        }
        for t in all_tasks
        if t.is_overdue
    ]

    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == 'done',
        Task.updated_at >= seven_days_ago,
    ).count()

    users = User.query.options(joinedload(User.tasks)).all()
    user_stats = []
    for user in users:
        total = len(user.tasks)
        completed = sum(1 for t in user.tasks if t.status == 'done')
        user_stats.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': calculate_percentage(completed, total),
        })

    return {
        'generated_at': str(datetime.now(timezone.utc)),
        'overview': {
            'total_tasks': total_tasks,
            'total_users': total_users,
            'total_categories': total_categories,
        },
        'tasks_by_status': {
            'pending': pending,
            'in_progress': in_progress,
            'done': done,
            'cancelled': cancelled,
        },
        'tasks_by_priority': {
            'critical': priority_counts[1],
            'high': priority_counts[2],
            'medium': priority_counts[3],
            'low': priority_counts[4],
            'minimal': priority_counts[5],
        },
        'overdue': {
            'count': len(overdue_list),
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }


def user_report(user_id):
    user = User.query.get(user_id)
    if not user:
        raise AppError('Usuário não encontrado', 404)

    tasks = Task.query.filter_by(user_id=user_id).all()

    status_counts = {'done': 0, 'pending': 0, 'in_progress': 0, 'cancelled': 0}
    high_priority = 0
    overdue = 0

    for task in tasks:
        if task.status in status_counts:
            status_counts[task.status] += 1
        if task.priority <= 2:
            high_priority += 1
        if task.is_overdue:
            overdue += 1

    total = len(tasks)
    return {
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        },
        'statistics': {
            'total_tasks': total,
            'done': status_counts['done'],
            'pending': status_counts['pending'],
            'in_progress': status_counts['in_progress'],
            'cancelled': status_counts['cancelled'],
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': calculate_percentage(status_counts['done'], total),
        },
    }


def list_categories():
    categories = Category.query.all()
    result = []
    for category in categories:
        data = category.to_dict()
        data['task_count'] = Task.query.filter_by(category_id=category.id).count()
        result.append(data)
    return result


def create_category(data):
    if not data:
        raise AppError('Dados inválidos', 400)

    name = data.get('name')
    if not name:
        raise AppError('Nome é obrigatório', 400)

    category = Category()
    category.name = name
    category.description = data.get('description', '')
    category.color = data.get('color', DEFAULT_COLOR)

    db.session.add(category)
    db.session.commit()
    return category.to_dict()


def update_category(cat_id, data):
    category = Category.query.get(cat_id)
    if not category:
        raise AppError('Categoria não encontrada', 404)

    if not data:
        raise AppError('Dados inválidos', 400)

    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']
    if 'color' in data:
        category.color = data['color']

    db.session.commit()
    return category.to_dict()


def delete_category(cat_id):
    category = Category.query.get(cat_id)
    if not category:
        raise AppError('Categoria não encontrada', 404)

    db.session.delete(category)
    db.session.commit()
    return {'message': 'Categoria deletada'}

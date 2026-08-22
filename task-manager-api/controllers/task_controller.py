from sqlalchemy.orm import joinedload

from database import db
from middlewares.error_handler import AppError
from models.category import Category
from models.task import Task
from models.user import User
from services.notification_service import NotificationService
from utils.helpers import process_task_data

notification_service = NotificationService()


def _serialize_with_relations(task):
    data = task.to_dict()
    data['user_name'] = task.user.name if task.user else None
    data['category_name'] = task.category.name if task.category else None
    return data


def list_tasks():
    tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
    return [_serialize_with_relations(t) for t in tasks]


def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        raise AppError('Task não encontrada', 404)
    return task.to_dict()


def create_task(data):
    if not data:
        raise AppError('Dados inválidos', 400)

    if not data.get('title'):
        raise AppError('Título é obrigatório', 400)

    parsed, error = process_task_data(data)
    if error:
        raise AppError(error, 400)

    user_id = parsed.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if not user:
            raise AppError('Usuário não encontrado', 404)

    category_id = parsed.get('category_id')
    if category_id:
        category = Category.query.get(category_id)
        if not category:
            raise AppError('Categoria não encontrada', 404)

    task = Task()
    task.title = parsed['title']
    task.description = parsed.get('description', '')
    task.status = parsed.get('status', 'pending')
    task.priority = parsed.get('priority', 3)
    task.user_id = user_id
    task.category_id = category_id
    task.due_date = parsed.get('due_date')
    task.tags = parsed.get('tags')

    db.session.add(task)
    db.session.commit()

    if task.user_id:
        notification_service.notify_task_assigned(task.user, task)

    return task.to_dict()


def update_task(task_id, data):
    task = Task.query.get(task_id)
    if not task:
        raise AppError('Task não encontrada', 404)

    if not data:
        raise AppError('Dados inválidos', 400)

    parsed, error = process_task_data(data)
    if error:
        raise AppError(error, 400)

    if 'user_id' in parsed:
        if parsed['user_id']:
            user = User.query.get(parsed['user_id'])
            if not user:
                raise AppError('Usuário não encontrado', 404)
        task.user_id = parsed['user_id']

    if 'category_id' in parsed:
        if parsed['category_id']:
            category = Category.query.get(parsed['category_id'])
            if not category:
                raise AppError('Categoria não encontrada', 404)
        task.category_id = parsed['category_id']

    for field in ('title', 'description', 'status', 'priority', 'due_date', 'tags'):
        if field in parsed:
            setattr(task, field, parsed[field])

    db.session.commit()
    return task.to_dict()


def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        raise AppError('Task não encontrada', 404)

    db.session.delete(task)
    db.session.commit()
    return {'message': 'Task deletada com sucesso'}


def search_tasks(query, status, priority, user_id):
    tasks = Task.query

    if query:
        tasks = tasks.filter(
            db.or_(
                Task.title.like(f'%{query}%'),
                Task.description.like(f'%{query}%'),
            )
        )

    if status:
        tasks = tasks.filter(Task.status == status)

    if priority:
        tasks = tasks.filter(Task.priority == int(priority))

    if user_id:
        tasks = tasks.filter(Task.user_id == int(user_id))

    return [t.to_dict() for t in tasks.all()]


def get_task_stats():
    return Task.compute_stats()

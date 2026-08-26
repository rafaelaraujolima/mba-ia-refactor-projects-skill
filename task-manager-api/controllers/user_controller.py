from database import db
from middlewares.error_handler import AppError
from models.task import Task
from models.user import User
from utils.helpers import MIN_PASSWORD_LENGTH, VALID_ROLES, sanitize_string, validate_email


def list_users():
    users = User.query.all()
    result = []
    for user in users:
        data = user.to_dict()
        data['task_count'] = len(user.tasks)
        result.append(data)
    return result


def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        raise AppError('Usuário não encontrado', 404)

    data = user.to_dict()
    data['tasks'] = [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]
    return data


def create_user(data):
    if not data:
        raise AppError('Dados inválidos', 400)

    name = sanitize_string(data.get('name'))
    email = sanitize_string(data.get('email'))
    password = data.get('password')
    role = data.get('role', 'user')

    if not name:
        raise AppError('Nome é obrigatório', 400)
    if not email:
        raise AppError('Email é obrigatório', 400)
    if not password:
        raise AppError('Senha é obrigatória', 400)

    if not validate_email(email):
        raise AppError('Email inválido', 400)

    if len(password) < MIN_PASSWORD_LENGTH:
        raise AppError(f'Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres', 400)

    if User.query.filter_by(email=email).first():
        raise AppError('Email já cadastrado', 409)

    if role not in VALID_ROLES:
        raise AppError('Role inválido', 400)

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    db.session.add(user)
    db.session.commit()
    return user.to_dict()


ADMIN_ONLY_FIELDS = {'role', 'active'}


def update_user(user_id, data, acting_user):
    user = User.query.get(user_id)
    if not user:
        raise AppError('Usuário não encontrado', 404)

    if not data:
        raise AppError('Dados inválidos', 400)

    is_owner = acting_user.id == user_id
    is_admin = acting_user.role == 'admin'
    if not (is_owner or is_admin):
        raise AppError('Acesso negado', 403)

    blocked = ADMIN_ONLY_FIELDS & data.keys()
    if blocked and not is_admin:
        raise AppError(
            f'Apenas administradores podem alterar: {", ".join(sorted(blocked))}', 403
        )

    if 'name' in data:
        user.name = data['name']

    if 'email' in data:
        if not validate_email(data['email']):
            raise AppError('Email inválido', 400)
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            raise AppError('Email já cadastrado', 409)
        user.email = data['email']

    if 'password' in data:
        if len(data['password']) < MIN_PASSWORD_LENGTH:
            raise AppError('Senha muito curta', 400)
        user.set_password(data['password'])

    if 'role' in data:
        if data['role'] not in VALID_ROLES:
            raise AppError('Role inválido', 400)
        user.role = data['role']

    if 'active' in data:
        user.active = data['active']

    db.session.commit()
    return user.to_dict()


def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        raise AppError('Usuário não encontrado', 404)

    Task.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    return {'message': 'Usuário deletado com sucesso'}


def get_user_tasks(user_id):
    user = User.query.get(user_id)
    if not user:
        raise AppError('Usuário não encontrado', 404)

    tasks = Task.query.filter_by(user_id=user_id).all()
    result = []
    for task in tasks:
        result.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'created_at': str(task.created_at),
            'due_date': str(task.due_date) if task.due_date else None,
            'overdue': task.is_overdue,
        })
    return result

from datetime import datetime, timezone

from database import db
from utils.helpers import VALID_STATUSES


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending')
    priority = db.Column(db.Integer, default=3)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'due_date': str(self.due_date) if self.due_date else None,
            'tags': self.tags.split(',') if self.tags else [],
            'overdue': self.is_overdue,
        }

    @staticmethod
    def validate_status(status):
        return status in VALID_STATUSES

    @staticmethod
    def validate_priority(priority):
        return 1 <= priority <= 5

    @property
    def due_date_aware(self):
        if not self.due_date:
            return None
        if self.due_date.tzinfo is None:
            return self.due_date.replace(tzinfo=timezone.utc)
        return self.due_date

    @property
    def is_overdue(self):
        due_date = self.due_date_aware
        if not due_date:
            return False
        return due_date < datetime.now(timezone.utc) and self.status not in ('done', 'cancelled')

    @staticmethod
    def compute_stats():
        total = Task.query.count()
        pending = Task.query.filter_by(status='pending').count()
        in_progress = Task.query.filter_by(status='in_progress').count()
        done = Task.query.filter_by(status='done').count()
        cancelled = Task.query.filter_by(status='cancelled').count()
        overdue = sum(1 for t in Task.query.all() if t.is_overdue)

        return {
            'total': total,
            'pending': pending,
            'in_progress': in_progress,
            'done': done,
            'cancelled': cancelled,
            'overdue': overdue,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
        }

import logging
from datetime import datetime, timezone

from flask import Flask
from flask_cors import CORS

from config import settings
from database import db
from middlewares.error_handler import register_error_handlers
from routes.report_routes import report_bp
from routes.task_routes import task_bp
from routes.user_routes import user_bp

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = settings.SECRET_KEY

CORS(app)
db.init_app(app)
register_error_handlers(app)

app.register_blueprint(task_bp)
app.register_blueprint(user_bp)
app.register_blueprint(report_bp)


@app.route('/health')
def health():
    return {'status': 'ok', 'timestamp': str(datetime.now(timezone.utc))}


@app.route('/')
def index():
    return {'message': 'Task Manager API', 'version': '1.0'}


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=settings.DEBUG, host='0.0.0.0', port=5000)

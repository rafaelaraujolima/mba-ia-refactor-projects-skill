from flask import Flask
from flask_cors import CORS

from src.config import settings
from src.middlewares.error_handler import register_error_handlers
from src.models.db import init_db
from src.routes.routes import register_routes


def create_app():
    """Composition root: monta a aplicação a partir de config, banco, rotas e middlewares."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG

    CORS(app)
    init_db(app)
    register_routes(app)
    register_error_handlers(app)

    return app

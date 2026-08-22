import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("A variável de ambiente SECRET_KEY é obrigatória")

DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
DB_PATH = os.environ.get("DB_PATH", "loja.db")

ADMIN_ROLE = "admin"

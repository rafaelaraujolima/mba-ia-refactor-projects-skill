import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError('SECRET_KEY environment variable is required')

DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///tasks.db')

JWT_ALGORITHM = 'HS256'
JWT_EXP_HOURS = int(os.environ.get('JWT_EXP_HOURS', '24'))

SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')

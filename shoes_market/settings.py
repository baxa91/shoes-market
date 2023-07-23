import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_PATH = os.getenv('MEDIA')
MEDIA = os.path.join(BASE_DIR, MEDIA_PATH)
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', False)

DATABASE_URL = os.getenv('DATABASE_URL')

JWT_ACCESS_TTL = 60 * 60 * 24
JWT_REFRESH_TTL = 60 * 60 * 24 * 30

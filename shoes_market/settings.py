import os


DEBUG = os.getenv('DEBUG', False)

DATABASE_URL = os.getenv('DATABASE_URL')

JWT_ACCESS_TTL = 60 * 60 * 24
JWT_REFRESH_TTL = 60 * 60 * 24 * 30

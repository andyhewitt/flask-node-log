import os
basedir = os.path.abspath(os.path.dirname(__file__))


POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
DATABASE_URL = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres:5432/books'


class BaseConfig:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    SQLALCHEMY_DATABASE_URI = DATABASE_URL


class ProductionConfig(BaseConfig):
    """Production configuration"""
    SQLALCHEMY_DATABASE_URI = DATABASE_URL

class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, 'database.db')
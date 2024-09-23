import os

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://Legnnit:frenchhorn@127.0.0.1:3307/Legnnit$tester'
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 280
    SQLALCHEMY_MAX_OVERFLOW = 2
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}

    # Secret Key for Session Management
    SECRET_KEY = os.environ.get('SECRET_KEY', 'development')

    # Other settings, like debug mode or mail settings can be added here
    DEBUG = True  # You can adjust this based on environment

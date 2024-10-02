class Config:
    # Common settings
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 280
    SQLALCHEMY_MAX_OVERFLOW = 2
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}
    SECRET_KEY = 'development'

class DevelopmentConfig(Config):
    # Development (local) database settings
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://Legnnit:frenchhorn@127.0.0.1:3307/Legnnit$tester'
    DEBUG = True

class ProductionConfig(Config):
    # Production (PythonAnywhere) database settings
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://Legnnit:frenchhorn@Legnnit.mysql.pythonanywhere-services.com/Legnnit$deployment'
    DEBUG = False

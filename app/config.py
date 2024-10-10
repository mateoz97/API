class Config:
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False


class DBconfig:
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'teo'
    MYSQL_PASSWORD = 'Kiminomichimade1997*'
    MYSQL_DATABASE = 'FLASKCRUD'
class Config:
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False


class DBconfig:
    MYSQL_HOST = '34.122.226.163'
    MYSQL_USER = 'teo'
    MYSQL_PASSWORD = 'Kiminomichimade1997*'
    MYSQL_DATABASE = 'GlobantAPI'
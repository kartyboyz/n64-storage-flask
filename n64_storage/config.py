

class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql:///n64_storage'


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    #SQLALCHEMY_DATABASE_URI 


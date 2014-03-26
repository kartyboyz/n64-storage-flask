

class Config(object):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://kartyboyz:kartzarecool@n64-database.cjkhmjv2ca1f.us-east-1.rds.amazonaws.com/n64data'
    AWS_ACCESS_KEY_ID = 'AKIAIAUU2RAXJQC52GSA'
    AWS_SECRET_ACCESS_KEY = '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'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql:///n64_storage'


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    #SQLALCHEMY_DATABASE_URI

class AWSConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://kartyboyz:kartzarecool@n64-database.cjkhmjv2ca1f.us-east-1.rds.amazonaws.com/n64data'

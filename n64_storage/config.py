
import os

class Config(object):
    DEBUG = True
    TESTING = False
    SEND_MESSAGES = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    RACE_PIPELINE = '1398306135448-eqvam9'
    SESS_PIPELINE = '1395885064713-5fx6l1'
    PRESET = '1351620000001-100070'
    AWS_REGION = 'us-east-1'
    SPLIT_QUEUE = 'split-queue'
    PROCESS_QUEUE = 'process-queue'
    AUTOSCALE_GROUP = 'video-processing-group'
    TRANSCODE = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@example.com/kartdata'


class TestingConfig(Config):
    DEBUG = True
    TESTING = True

class AWSConfig(Config):
    DEBUG = True
    SEND_MESSAGES = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE', '')
    TRANSCODE = True

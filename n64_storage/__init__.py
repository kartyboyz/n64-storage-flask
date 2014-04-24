
import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate
from flask.ext.restful import Api

app = Flask(__name__)



from . import models
from . import object_api
from . import video_api
from . import tests
from . import query
from . import parser

api = Api()

def configure():
    env = os.environ.get('CONFIG_MODULE', 'n64_storage.config.Config')
    app.config.from_object(env)

    api.init_app(app)

    models.init_db(app)
    object_api.configure_resources(api)

    if app.config['SEND_MESSAGES']:
        object_api.connect_sqs(app)



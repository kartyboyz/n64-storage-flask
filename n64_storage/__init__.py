
import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate
from flask.ext.restful import Api

app = Flask(__name__)

env = os.environ.get('CONFIG_MODULE', 'n64_storage.config.Config')
app.config.from_object(env)


from . import models
from . import object_api
from . import video_api

api = Api()

def init_api():
    api.init_app(app)

init_api()
models.init_db(app)
object_api.configure_resources(api)
object_api.connect_sqs(app)
video_api.configure_resources(api)


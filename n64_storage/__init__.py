
import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate

app = Flask(__name__)

env = os.environ.get('CONFIG_MODULE', 'n64_storage.config.Config')
app.config.from_object(env)


from . import models                            
from . import api

api.init_api(app)
api.configure_resources()
models.init_db(app)


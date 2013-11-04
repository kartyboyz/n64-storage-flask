
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///n64_storage'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from . import models                            


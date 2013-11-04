#!/usr/bin/env python

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from n64_storage import app, db, models

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.shell
def shell_context():
    return dict(app=app, db=db, models=models)

if __name__ == '__main__':
    manager.run()


#!/usr/bin/env python

import sys, os
import nose

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand


if len(sys.argv) > 1 and sys.argv[1] == 'runtests' and not 'CONFIG_MODULE' in os.environ:
    os.environ['CONFIG_MODULE'] = 'n64_storage.config.TestingConfig'
elif 'CONFIG_MODULE' not in os.environ:
    os.environ['CONFIG_MODULE'] = 'n64_storage.config.DevelopmentConfig'


from n64_storage import app, models, api

migrate = Migrate(app, models.db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.shell
def shell_context():
    return dict(app=app, api=api, models=models)

@manager.command
def runtests():
    del sys.argv[1]
    nose.run()

if __name__ == '__main__':
    manager.run()


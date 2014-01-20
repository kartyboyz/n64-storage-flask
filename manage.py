#!/usr/bin/env python

import sys, os
import nose

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

orig_argv = sys.argv[:]


if len(sys.argv) > 1 and sys.argv[1] == 'runtests' and not 'CONFIG_MODULE' in os.environ:
    nose_args = sys.argv[1:]
    del nose_args[0]
    if len(sys.argv) > 2:
        del sys.argv[2:]
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
    #del sys.argv[1]
    #sys.argv.extend(nose_args)
    argv=orig_argv[:]
    del argv[1]
    argv[0] = 'nosetests'
    nose.run(argv=argv)

if __name__ == '__main__':
    manager.run()


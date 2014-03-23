#!/usr/bin/python

import n64_storage

application = n64_storage.app

if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)

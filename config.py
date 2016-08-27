"""
A set of configuration settings for the web app
"""

import os

WTF_CSRF_ENABLED = True
SECRET_KEY = 'someComplexString'

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

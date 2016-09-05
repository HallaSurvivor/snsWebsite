"""
A set of configuration settings for the web app
"""

import os

# Tell Flask that we want to protect against CSRF attacks
WTF_CSRF_ENABLED = True

# The secret key to use to generate the protection against CSRF attacks
# PLEASE FOR THE LOVE OF GOD MAKE THIS COMPLEX AND ALPHANUMERIC
SECRET_KEY = 'someComplexString'

# The base directory of the project
basedir = os.path.abspath(os.path.dirname(__file__))

# The location of the database file
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

# We don't need sqlalchemy to track our changes for us
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Email support!!!
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_ADDRESS = os.environ.get('MAIL_ADDRESS')

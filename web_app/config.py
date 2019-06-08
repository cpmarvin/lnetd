import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
SECRET_KEY = 'secret_key_here'
DEBUG = True
USER_ENABLE_EMAIL = False
USER_ENABLE_USERNAME = True
USER_REQUIRE_RETYPE_PASSWORD = False

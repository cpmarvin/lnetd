from flask import Flask, render_template, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module

from inspect import stack
from logging import Formatter, FileHandler

from os.path import abspath, dirname, join
from objects_v2.models import App_config

import logging
import os
import sys


# prevent python from writing *.pyc files / __pycache__ folders
sys.dont_write_bytecode = True

path_app = dirname(abspath(stack()[0][1]))
if path_app not in sys.path:
    sys.path.append(path_app)

path_source = os.path.dirname(os.path.abspath(__file__))

from database import db, create_database
from base_v2.routes import login_manager
from base_v2.models import User


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in (
        "api_v2",
        "objects_v2",
        "home_v2",
        "data_v2",
        "base_v2",
        "admin_v2",
        "map_v2",
        "inventory_v2",
        "bgp_v2",
        "dc_v2",
        "prov_v2",
        "noc_v2",
    ):
        module = import_module("{}.routes".format(module_name))
        app.register_blueprint(module.blueprint)


def configure_login_manager(app, User):
    @login_manager.user_loader
    def user_loader(id):
        return db.session.query(User).filter_by(id=id).first()

    @login_manager.request_loader
    def request_loader(request):
        username = request.form.get("username")
        user = db.session.query(User).filter_by(username=username).first()
        return user if user else None


def configure_database(app):
    create_database()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()

    migrate = Migrate(app, db)


def configure_logs(app):
    if not app.debug:
        logging.basicConfig(filename="error.log", level=logging.DEBUG)
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())


def create_app(config="config"):
    app = Flask(__name__, static_folder="base_v2/static")
    app.config.from_object("config")

    register_extensions(app)
    register_blueprints(app)
    # register_azure_extention(app)
    from base_v2.models import User

    configure_login_manager(app, User)
    configure_database(app)
    configure_logs(app)

    return app


app = create_app()


@app.context_processor
def get_app_config():

    app_config = App_config.query.all()
    return dict(app_config=app_config[0])


@app.errorhandler(404)
def global_404(e):
    return redirect(url_for("home_blueprint.index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8801)), threaded=True)

import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_login import LoginManager

# instantiate the extensions
db = SQLAlchemy()
migrate = Migrate()


def make_nav_bar(env):
    bar = (
        {
            "name": "prod",
            "text": "Production clusters",
            "url": "/prod",
            "active": "",
        },
        {
            "name": "qa",
            "text": "QA clusters",
            "url": "/qa",
            "active": "",
        }
    )
    for item in bar:
        if item["name"] == env:
            item["active"] = "active"
    return bar


def create_app(script_info=None):
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    # instantiate the app
    app = Flask(__name__, template_folder="templates")
    app.secret_key = b'7a6a4deee1175214e57cd3c7ee2a033ca90b2dc1809522e4'

    # enable CORS
    CORS(app)

    # set config
    app_settings = os.getenv("APP_SETTINGS", "project.config.TestingConfig")
    app.config.from_object(app_settings)

    app.config['WTF_CSRF_SECRET_KEY'] = 'random key for form'
    app.config['LDAP_PROVIDER_URL'] = 'ldap://ldap.forumsys.com:389/'
    app.config['LDAP_PROTOCOL_VERSION'] = 3

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # set up extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # register blueprints
    from project.api.nodes import nodes_blueprint
    app.register_blueprint(nodes_blueprint)

    # blueprint for auth routes in our app
    from project.api.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from project.api.models import User

    @login_manager.user_loader
    def load_user(id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(id))

    # # shell context for flask cli
    # @app.shell_context_processor
    # def ctx():
    #     return {'app': app, 'db': db}

    return app

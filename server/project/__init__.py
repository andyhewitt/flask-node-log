import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate


# instantiate the extensions
db = SQLAlchemy()
migrate = Migrate()

def make_nav_bar(env):
    bar =  (
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
    app.secret_key = os.urandom(12).hex()

    # enable CORS
    CORS(app)

    # set config
    app_settings = os.getenv("APP_SETTINGS", "project.config.TestingConfig")
    app.config.from_object(app_settings)

    # set up extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # register blueprints
    from project.api.nodes import nodes_blueprint
    app.register_blueprint(nodes_blueprint)

    # # shell context for flask cli
    # @app.shell_context_processor
    # def ctx():
    #     return {'app': app, 'db': db}

    return app

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate


# instantiate the extensions
db = SQLAlchemy()
migrate = Migrate()


def create_app(script_info=None):

    # instantiate the app
    app = Flask(__name__, template_folder="templates")

    # enable CORS
    CORS(app)

    # # set config
    # app_settings = os.getenv('APP_SETTINGS')
    # app.config.from_object(app_settings)

    # basedir = os.path.abspath(os.path.dirname(__file__))

    POSTGRES_USER = os.environ.get('POSTGRES_USER')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres:5432/nodes'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

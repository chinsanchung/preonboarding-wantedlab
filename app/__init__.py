from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api

import config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)
    from . import models

    # flask_restx
    api = Api(app)

    from .companies import companies_controller as company
    from .search import search_controller as search

    api.add_namespace(company.ns, "/companies")
    api.add_namespace(search.ns, "/search")

    return app

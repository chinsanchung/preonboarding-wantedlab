from flask import Flask
from flask_restx import Api
import config
from database import db, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # ORM
    from resources import models

    db.init_app(app)
    migrate.init_app(app, db)

    # flask_restx
    from resources.main import main_controller as main
    from resources.companies import companies_controller as companies
    from resources.search import search_controller as search

    api = Api(app)

    api.add_namespace(main.ns, "/")
    api.add_namespace(companies.ns, "/companies")
    api.add_namespace(search.ns, "/search")

    return app


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(host="0.0.0.0", port=5000)

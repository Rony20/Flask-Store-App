import os
from flask import Flask
from flask_smorest import Api

import models
from db import db
from resources.item import blp as item_blue_print
from resources.store import blp as store_blue_print

# Run the following command to set docker volume on particular image
# docker run -dp 8000:5000 -w /app -v "$(pwd):/app" flask-smorest-api


def create_app(db_url=None):
    app = Flask(__name__)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    api = Api(app)

    # TODO: Check app_context method
    with app.app_context():
        db.create_all()

    api.register_blueprint(store_blue_print)
    api.register_blueprint(item_blue_print)

    return app

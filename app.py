import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_smorest import Api
from flask_migrate import Migrate

import models

from db import db
from models import BlockListModel
from resources.item import blp as item_blue_print
from resources.store import blp as store_blue_print
from resources.tag import blp as tag_blue_print
from resources.user import blp as user_blue_print

# Run the following command to set docker volume on particular image
# docker run -dp 8000:5000 -w /app -v "$(pwd):/app" flask-smorest-api


def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate = Migrate(app, db)

    api = Api(app)

    app.config["JWT_SECRET_KEY"] = "43427464583166506109419722629133463570009142403819322148911687990523731930688"
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        if BlockListModel.query.filter(BlockListModel.token == jwt_payload["jti"]).first():
            return True
        return False

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"description": "The token has been revoked.", "error": "token_revoked"}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"message": "Signature verification failed.", "error": "invalid_token"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify({"message": "Request does not contain an access token.", "error": "authorization_required"}), 401)

    # TODO: Check app_context method
    # with app.app_context():
    #     db.create_all()

    api.register_blueprint(store_blue_print)
    api.register_blueprint(item_blue_print)
    api.register_blueprint(tag_blue_print)
    api.register_blueprint(user_blue_print)

    return app

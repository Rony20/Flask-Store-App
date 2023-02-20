import os
import requests

from flask.views import MethodView
from flask_smorest import abort, Blueprint
from flask_jwt_extended import create_access_token, get_jwt
from flask_jwt_extended import jwt_required
from passlib.hash import pbkdf2_sha256
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import BlockListModel, UserModel
from schemas import UserRegisterSchema, UserSchema


blp = Blueprint("Users", __name__, description="Operations on users")


def send_simple_message(to, subject, body):
    domain = os.getenv("MAILGUN_DOMAIN")
    api_key = os.getenv("MAILGUN_API_KEY")
    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", api_key),
        data={
            "from": f"Rohan Borkhatariya <mailgun@{domain}>",
            "to": [to],
            "subject": subject,
            "text": body
        })


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201)
    def post(self, user_data):
        if UserModel.query.filter(
                or_(
                    UserModel.username == user_data["username"],
                    UserModel.email == user_data["email"]
                )).first():
            abort(409, message="A user with that username or email already exists.")

        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"]),
            email=user_data["email"]
        )

        try:
            db.session.add(user)
            db.session.commit()
            send_simple_message(
                user.email, "Successfully signed up",
                f"Hi {user.username}! You have successfully signed up to the Stores REST API")
        except SQLAlchemyError:
            abort(500, message="An error occurred while creating an user")

        return {"message": "User created successfully."}


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(200)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.username == user_data["username"]).first()
        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id)
            return {"access_token": access_token}
        abort(401, "invalid credentials.")


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    @blp.response(200)
    def post(self):
        jti = get_jwt()["jti"]
        blocklist_item = BlockListModel(token=jti)

        try:
            db.session.add(blocklist_item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while blacklisting the token")

        return {"message": "Successfully logged out."}


@blp.route("/user/<int:user_id>")
class User(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    @jwt_required()
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)

        try:
            db.session.delete(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting an user")

        return {"message": "User deleted successfully."}

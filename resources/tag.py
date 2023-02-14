from flask.views import MethodView
from flask_smorest import abort, Blueprint
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db import db
from models import TagModel, StoreModel
from schemas import TagSchema

blp = Blueprint("tags", __name__, "Operations tags")


@blp.route("/store/<string:store_id>/tag")
class TagInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        if TagModel.query.filter(TagModel.store_id == store_id, TagModel.name == tag_data["name"]).first():
            abort(400, message="Tag with given name already exists in the store.")

        tag = TagModel(**tag_data, store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except IntegrityError as e:
            abort(400, message="Tag with this name already exist.")
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return tag


@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag


@blp.route("/tag")
class TagList(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self):
        return TagModel.query.all()

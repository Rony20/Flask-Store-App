from db import db
from flask.views import MethodView
from flask_smorest import abort, Blueprint
from models import ItemModel
from sqlalchemy.exc import SQLAlchemyError

from schemas import ItemSchema, ItemUpdateSchema

blp = Blueprint("Items", __name__, "Operations related to items")


@blp.route("/item/<int:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    def delete(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted."}

    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    # TODO: Check how the put method should behave
    def put(self, item_data, item_id):
        item = ItemModel.query.get(item_id)

        if item:
            item_price = item_data.get("price", None)
            item_name = item_data.get("name", None)
            item_store_id = item_data.get("store_id", None)
            if item_price:
                item.price = item_price
            if item_name:
                item.name = item_name
            if item_store_id:
                item.store_id = item_store_id
        else:
            item = ItemModel(id=item_id, **item_data)

        try:
            db.session.add(item)
            db.session.commit()
            return item
        except SQLAlchemyError:
            abort(500, "An error occurred while updating the item.")


@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        item = ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting an item.")

        return item

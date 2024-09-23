from flask import jsonify, Blueprint
from pymongo import MongoClient

test_db_blueprint = Blueprint('test_db', __name__)


client = MongoClient("mongodb+srv://reyanjimenez:mjWiDjrreHl66MuY@consultor-api-db.tqpkb.mongodb.net/?retryWrites=true&w=majority&appName=consultor-api-db")
db = client["test"]
collection = db["gama"]

@test_db_blueprint.route('/test', methods=['GET'])
def dbtest():
    categorias = collection.find({"results": {"$exists": True}})
    for categoria in categorias:
        print(categoria)
    return jsonify(list(categorias))
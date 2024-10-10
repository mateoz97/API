
from flask import Blueprint, jsonify, request
from app.views import get_all_products

products_bp = Blueprint('products', __name__)

@products_bp.route('/ping')
def ping():
    return jsonify({"message": "Pong!"})


@products_bp.route('/products', methods=['GET'])
def get_products():
    return get_all_products()

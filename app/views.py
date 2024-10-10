from flask import Blueprint, jsonify, request, current_app
from app.models import Product


def get_all_products():
    cursor = current_app.db.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    products = [Product.from_db(row).__dict__ for row in rows]
    return jsonify(products)

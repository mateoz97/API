
from flask import Blueprint, jsonify, request
from app.views import getDataTable, post_data, backupAVRO

products_bp = Blueprint('products', __name__)

@products_bp.route('/ping')
def ping():
    return jsonify({"message": "Pong!"})


@products_bp.route('/table/<table_name>', methods=['GET'])
def get_tables(table_name):
    return getDataTable(table_name)


@products_bp.route('/uploadCSV', methods=['POST'])
def post_data_ingest():
    return post_data()

@products_bp.route('/backup/<table_name>', methods=['POST'])
def backup(table_name):
    if table_name not in ['departments', 'jobs', 'hired_employed']:
        return jsonify({"error": "Invalid table name"}), 400

    result = backupAVRO(table_name)
    return jsonify({"message": result}), 200
from flask import Blueprint, jsonify, request, current_app
from app.models import Product, Departaments, Jobs, HiredEmployed
import pandas as pd


def get_all_products():
    cursor = current_app.db.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    products = [Product.from_db(row).__dict__ for row in rows]
    return jsonify(products)

def post_data():
     
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']

    
    if file.filename == '':
        return "No selected file", 400

    
    if not file.filename.endswith('.csv'):
        return "File is not a CSV", 400

    
    try:
        df = pd.read_csv(file, header=None, names=['departament_id', 'departament_name'])
        print(df)
    except Exception as e:
        return f"Error reading CSV: {str(e)}", 400

    return "CSV file received and printed", 200
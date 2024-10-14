from flask import Blueprint, jsonify, request, current_app
from app.models import Product, Departments, Jobs, HiredEmployed
import pandas as pd
import mysql.connector
import numpy as np


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
    
    # Verificar si el archivo fue seleccionado
    if file.filename == '':
        return "No selected file", 400
    
    # Obtener el nombre de la tabla
    table_name = request.form.get('table')
    if table_name not in ['departments', 'jobs', 'hired_employed']:
        return jsonify({"error": "Invalid table name"}), 400

    # Verificar que el archivo sea un CSV
    if not file.filename.endswith('.csv'):
        return "File is not a CSV", 400

    try:
        # Leer el archivo CSV
        if table_name == 'departments':
            df = pd.read_csv(file,header=None, names=['departament_id', 'departament_name'])
        elif table_name == 'jobs':
            df = pd.read_csv(file,header=None, names=['job_id', 'job_name'])
        else:
            df = pd.read_csv(file,header=None, names=['id', 'employee_name','date_hired','departament_id','job_id'])
            # Convertir la columna 'date_hired' a un formato compatible con MySQL
            df['date_hired'] = pd.to_datetime(df['date_hired'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')

        # Reemplazar NaN y valores vacíos con None
        df = df.where(pd.notnull(df), None)

        
        df = df.replace({np.nan: None})

        cursor = current_app.db.cursor()
        # Obtener las columnas del CSV
        csv_columns = df.columns.tolist()

        # Verificar las columnas válidas según la tabla
        cursor.execute(f"DESCRIBE {table_name}")
        table_columns = [column[0] for column in cursor.fetchall()]
        valid_columns = [col for col in csv_columns if col in table_columns]

        if not valid_columns:
            return jsonify({"error": "No valid columns in CSV"}), 400

        placeholders = ", ".join(["%s"] * len(valid_columns))
        columns_str = ", ".join(valid_columns)
        insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

        for _, row in df.iterrows():
            values = tuple(row[col] for col in valid_columns)
            cursor.execute(insert_query, values)

        current_app.db.commit()

        return jsonify({"message": f"CSV data uploaded successfully to {table_name}"}), 201

    except mysql.connector.Error as err:
        current_app.db.rollback()
        return jsonify({"error": f"Database error: {str(err)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error processing CSV: {str(e)}"}), 400

    finally:
        if cursor:
            cursor.close()
        if current_app.db:
            current_app.db.close()

    return jsonify({"error": "Invalid file format"}), 400
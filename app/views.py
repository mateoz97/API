from flask import Blueprint, jsonify, request, current_app
from app.models import  Departments, Jobs, HiredEmployed
import pandas as pd
import mysql.connector
import numpy as np


def get_all_products():
    pass
    # cursor = current_app.db.cursor()
    # cursor.execute("SELECT * FROM products")
    # rows = cursor.fetchall()
    # products = [Product.from_db(row).__dict__ for row in rows]
    # return jsonify(products)


def validate_data(table_name, row):
    if table_name == 'departments':
        if not isinstance(row['departament_id'], int) or not isinstance(row['departament_name'], str):
            return False
    elif table_name == 'jobs':
        if not isinstance(row['job_id'], int) or not isinstance(row['job_name'], str):
            return False
    elif table_name == 'hired_employed':
        if row['id'] is None or not isinstance(row['id'], int):
            return False
        if row['employee_name'] is not None and not isinstance(row['employee_name'], str):
            return False
        if row['date_hired'] is not None and not isinstance(row['date_hired'], str):
            return False
        if row['departament_id'] is not None and not isinstance(row['departament_id'], int):
            return False
        if row['job_id'] is not None and not isinstance(row['job_id'], int):
            return False
    return True


def post_data():

    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    

    if file.filename == '':
        return "No selected file", 400
    

    table_name = request.form.get('table')
    if table_name not in ['departments', 'jobs', 'hired_employed']:
        return jsonify({"error": "Invalid table name"}), 400

    if not file.filename.endswith('.csv'):
        return "File is not a CSV", 400

    try:
        if table_name == 'departments':
            df = pd.read_csv(file,header=None, names=['departament_id', 'departament_name'])
        elif table_name == 'jobs':
            df = pd.read_csv(file,header=None, names=['job_id', 'job_name'])
        else:
            df = pd.read_csv(file,header=None, names=['id', 'employee_name','date_hired','departament_id','job_id'])
            df['date_hired'] = pd.to_datetime(df['date_hired'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
            df['departament_id'] = df['departament_id'].fillna(0).astype(int).replace(0, None)
            df['job_id'] = df['job_id'].fillna(0).astype(int).replace(0, None)


        df = df.where(pd.notnull(df), None)

        
        df = df.replace({np.nan: None})

        cursor = current_app.db.cursor()

        for _, row in df.iterrows():
            if not validate_data(table_name, row):
                return jsonify({"error": f"Invalid data in row: {row.to_dict()}"}), 400


        csv_columns = df.columns.tolist()
        cursor.execute(f"DESCRIBE {table_name}")
        table_columns = [column[0] for column in cursor.fetchall()]
        valid_columns = [col for col in csv_columns if col in table_columns]

        if not valid_columns:
            return jsonify({"error": "No valid columns in CSV"}), 400

        placeholders = ", ".join(["%s"] * len(valid_columns))
        columns_str = ", ".join(valid_columns)
        insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"


        batch_size = 1000
        rows_to_insert = [tuple(row[col] for col in valid_columns) for _, row in df.iterrows()]
        
        for i in range(0, len(rows_to_insert), batch_size):
            batch = rows_to_insert[i:i + batch_size]
            cursor.executemany(insert_query, batch)
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
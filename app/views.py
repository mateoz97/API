from flask import Blueprint, jsonify, request, current_app, abort
import pandas as pd
import mysql.connector
import numpy as np
import os
import fastavro
import datetime

BACKUP_DIR = 'data/backup'

def getDataTable(table_name):
    valid_tables = ['departments', 'jobs', 'hired_employed']
    
    if table_name not in valid_tables:
        return jsonify({"error": "Invalid table name"}), 400

    cursor = current_app.db.cursor()

    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        return jsonify(data)

    except mysql.connector.Error as err:
        abort(500, description=f"Database error: {str(err)}")
    finally:
        cursor.close()


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
            df = pd.read_csv(file, header=None, names=['departament_id', 'departament_name'])
        elif table_name == 'jobs':
            df = pd.read_csv(file, header=None, names=['job_id', 'job_name'])
        else:
            df = pd.read_csv(file, header=None, names=['id', 'employee_name', 'date_hired', 'departament_id', 'job_id'])
            df['date_hired'] = pd.to_datetime(df['date_hired'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
            df['departament_id'] = df['departament_id'].fillna(0).astype(int).replace(0, None)
            df['job_id'] = df['job_id'].fillna(0).astype(int).replace(0, None)

        df = df.where(pd.notnull(df), None)
        df = df.replace({np.nan: None})

        cursor = current_app.db.cursor()

        # Procesar registros en lotes de 1000
        batch_size = 1000
        rows_to_insert = [tuple(row[col] for col in df.columns) for _, row in df.iterrows()]
        
        for i in range(0, len(rows_to_insert), batch_size):
            batch = rows_to_insert[i:i + batch_size]
            filtered_batch = []

            for row in batch:
                # Verificar si el 'id' ya existe en la tabla antes de insertar
                if table_name == 'hired_employed':
                    cursor.execute("SELECT COUNT(*) FROM hired_employed WHERE id = %s", (row[0],))
                    result = cursor.fetchone()
                    if result[0] == 0:  # Si el id no existe, agregar a filtered_batch
                        filtered_batch.append(row)
                else:
                    filtered_batch.append(row)

            if filtered_batch:
                # Preparar la consulta de inserción para solo los registros no duplicados
                csv_columns = df.columns.tolist()
                placeholders = ", ".join(["%s"] * len(csv_columns))
                columns_str = ", ".join(csv_columns)
                insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                
                cursor.executemany(insert_query, filtered_batch)
        
        current_app.db.commit()
        return jsonify({"message": f"CSV data uploaded successfully to {table_name}, skipping duplicates"}), 201

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


def backupAVRO(table_name):
    cursor = None
    try:
        cursor = current_app.db.cursor(dictionary=True)

        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        if not rows:
            return f"No data found in table {table_name}."


        cursor.execute(f"DESCRIBE {table_name}")
        table_description = cursor.fetchall()
        schema_fields = []
        for column in table_description:
            column_name = column['Field']
            column_type = column['Type']
            if 'int' in column_type:
                schema_fields.append({'name': column_name, 'type': ['null', 'int']})
            elif 'float' in column_type or 'double' in column_type:
                schema_fields.append({'name': column_name, 'type': ['null', 'float']})
            elif 'varchar' in column_type or 'text' in column_type or 'char' in column_type:
                schema_fields.append({'name': column_name, 'type': ['null', 'string']})
            elif 'date' in column_type or 'datetime' in column_type:
                schema_fields.append({'name': column_name, 'type': ['null', 'string']})
            else:
                schema_fields.append({'name': column_name, 'type': ['null', 'string']})

        schema = {
            'name': table_name,
            'type': 'record',
            'fields': schema_fields
        }


        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)


        backup_file = os.path.join(BACKUP_DIR, f"{table_name}.avro")


        for row in rows:
            for key, value in row.items():
                if isinstance(value, datetime.datetime):
                    row[key] = value.strftime('%Y-%m-%d %H:%M:%S')  


        with open(backup_file, 'wb') as out:
            fastavro.writer(out, schema, rows)  

        return f"Backup for table {table_name} saved as {backup_file}"

    except mysql.connector.Error as err:
        return f"Database error: {str(err)}"
    except Exception as e:
        return f"Error during backup: {type(e).__name__} - {str(e)}"
    finally:
        if cursor:
            cursor.close()

def restoreAVRO(table_name):
    if table_name not in ['departments', 'jobs', 'hired_employed']:
        return jsonify({"error": "Invalid table name"}), 400

    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({"error": "No file part or empty filename"}), 400

    file = request.files['file']

    if not file.filename.endswith('.avro'):
        return jsonify({"error": "File is not an AVRO"}), 400

    try:
        reader = fastavro.reader(file)
        cursor = current_app.db.cursor()

        for record in reader:
            columns = ', '.join(record.keys())
            placeholders = ', '.join(['%s'] * len(record))
            insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

            cursor.execute(insert_query, list(record.values()))

        current_app.db.commit()
        return jsonify({"message": f"Data restored successfully to {table_name}"}), 201

    except mysql.connector.Error as err:
        current_app.db.rollback()
        return jsonify({"error": f"Database error: {str(err)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error restoring data: {str(e)}"}), 400
    finally:
        if cursor:
            cursor.close()

def getReportQuarter(year):
    cursor = None
    try:
        cursor = current_app.db.cursor(dictionary=True)

        if not year.isdigit() or len(year) != 4:
            return jsonify({"error": "Invalid year format"}), 400

        query = """
        SELECT 
          d.departament_name,
          p.job_name,
          COUNT(CASE WHEN EXTRACT(QUARTER FROM he.date_hired) = 1 THEN he.id END) AS Q1,
          COUNT(CASE WHEN EXTRACT(QUARTER FROM he.date_hired) = 2 THEN he.id END) AS Q2,
          COUNT(CASE WHEN EXTRACT(QUARTER FROM he.date_hired) = 3 THEN he.id END) AS Q3,
          COUNT(CASE WHEN EXTRACT(QUARTER FROM he.date_hired) = 4 THEN he.id END) AS Q4
        FROM hired_employed he
        JOIN jobs p ON he.job_id = p.job_id
        JOIN departments d ON he.departament_id = d.departament_id
        WHERE EXTRACT(YEAR FROM he.date_hired) = %s
        GROUP BY d.departament_name, p.job_name
        ORDER BY d.departament_name, p.job_name;
        """

        cursor.execute(query, (year,))
        rows = cursor.fetchall()

        if not rows:
            return jsonify({"message": f"No data found for year {year}."}), 404

        return jsonify(rows)

    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {str(err)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error during processing: {type(e).__name__} - {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()

def getReportDepart(year):
    cursor = None
    try:
        cursor = current_app.db.cursor(dictionary=True)

        if not year.isdigit() or len(year) != 4:
            return jsonify({"error": "Invalid year format"}), 400

        query = """
        WITH department_hires AS (
            SELECT 
                d.departament_id AS id,
                d.departament_name AS department,
                COUNT(he.id) AS hired
            FROM hired_employed he
            JOIN departments d ON he.departament_id = d.departament_id
            WHERE EXTRACT(YEAR FROM he.date_hired) = %s
            GROUP BY 1,2
        ), average_hires AS (
            SELECT 
            AVG(hired) AS avg_hired
            FROM department_hires
        )
        SELECT 
            dh.id,
            dh.department,
            dh.hired
        FROM department_hires dh
        JOIN average_hires ah ON dh.hired > ah.avg_hired
        ORDER BY 3 DESC;
        """

        cursor.execute(query, (year,))
        rows = cursor.fetchall()

        if not rows:
            return jsonify({"message": f"No data found for year {year}."}), 404

        return jsonify(rows)

    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {str(err)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error during processing: {type(e).__name__} - {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
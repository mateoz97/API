# API: Management of Departments, Jobs, and Hired Employees

## Introduction
This API allows managing **departments**, **jobs**, and **hired employees** tables, with the ability to upload CSV data, perform backups, and restore tables. The project uses a MySQL database.

## Data Model and Tables
### SQL Table Creation
Below are the SQL queries needed to create the database tables:

#### `departments` Table
```sql
CREATE TABLE departments (
    departament_id INT AUTO_INCREMENT PRIMARY KEY,
    departament_name VARCHAR(255) NOT NULL
);
```

#### `jobs` Table
```sql
CREATE TABLE jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    job_name VARCHAR(255) NOT NULL UNIQUE
);
```

#### `hired_employed` Table
```sql
CREATE TABLE hired_employed (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_name VARCHAR(255) NULL,
    date_hired DATETIME NULL,
    departament_id INT,
    job_id INT,
    CONSTRAINT fk_departament
        FOREIGN KEY (departament_id) REFERENCES departments(departament_id),
    CONSTRAINT fk_job
        FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);
```

## API Endpoints
### 1. Get Table Data
This endpoint allows you to view the content of any table in JSON format.

Endpoint: `GET /tables/<table_name>`

Example:
```bash
curl -X GET http://127.0.0.1:5000/tables/<table_name>
```


### 2. Upload a CSV File to Insert Data into a Table
This endpoint allows you to upload a .CSV file and insert its data into a specific database table.

Endpoint: `POST /uploadCSV`

Parameters:

- file: CSV file to upload.
- table: name of the table where the data will be inserted.

Example:

```bash
curl -X POST -F "file=@data/name_file.csv" -F "table=name_table" http://127.0.0.1:5000/uploadCSV
```


### 3. Backup a Table
This endpoint allows you to backup a table in AVRO format.

Endpoint: `POST /backup/<table_name>`

Example:

```bash
curl -X POST http://127.0.0.1:5000/backup/<table_name>
```

### 4. Restore a Table from Backup
This endpoint allows you to restore a table from a previously generated backup file.

Endpoint: `POST /restore/<table_name>`

Example:

```bash
curl -X POST http://127.0.0.1:5000/restore/<table_name>
```

## Installation and Dependencies
This project was set up using Poetry, which is used for managing dependencies and environments in Python projects. The dependencies include:

- Flask: The framework for building the web API.
- MySQL: The relational database used to store the data.
- mysql-connector-python: Used for directly connecting to the MySQL database, as an alternative to SQLAlchemy.
- Pandas: For CSV processing.
- fastavro: For handling AVRO format backups.

### Installation Steps:
#### Clone the repository.
1. Install Poetry if not already installed on your system:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install the project dependencies using Poetry:

```bash
poetry install
```

3. Activate the virtual environment created by Poetry:
```bash
poetry shell
```

4. Configure the database connection in the configuration file.
Run the Flask server:
```bash
python main.py
```

## Important Note
This project uses mysql-connector-python instead of SQLAlchemy for database interaction. This decision was made due to complications encountered when installing SQLAlchemy on Ubuntu. By using mysql-connector-python, we saved time and avoided potential compatibility issues, while still maintaining an efficient way to handle database connections and queries.


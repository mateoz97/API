# API: Management of Departments, Jobs, and Hired Employees

## Introduction
This API allows managing **departments**, **jobs**, and **hired employees** tables, with the ability to upload CSV data, perform backups, and restore tables. The project uses a MySQL database.

## Architecture

![Architecture API](image/globantapi.drawio.svg)


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

#### Challenged #2
Number of employees hired for each job and department in 2021 divided by quarter. The
table must be ordered alphabetically by department and job.
```sql
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
WHERE EXTRACT(YEAR FROM he.date_hired) = 2021
GROUP BY 1,2
ORDER BY 1,2
```

List of ids, name and number of employees hired of each department that hired more
employees than the mean of employees hired in 2021 for all the departments, ordered
by the number of employees hired (descending).
```sql
WITH department_hires AS (
    SELECT 
        d.departament_id AS id,
        d.departament_name AS department,
        COUNT(he.id) AS hired
    FROM hired_employed he
    JOIN departments d ON he.departament_id = d.departament_id
    WHERE EXTRACT(YEAR FROM he.date_hired) = 2021
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

```

# Analytics Report

You can dashboard report [here](https://lookerstudio.google.com/reporting/da96f343-4313-4d8b-89f6-7f91170e485a).




## API Endpoints
### 1. Get Table Data
This endpoint allows you to view the content of any table in JSON format.

Endpoint: `GET /tables/<table_name>`

Example:
```bash
curl -X GET https://globantapi-565552294938.us-central1.run.app/table/<table_name>
```


### 2. Upload a CSV File to Insert Data into a Table
This endpoint allows you to upload a .CSV file and insert its data into a specific database table.

Endpoint: `POST /uploadCSV`

Parameters:

- file: CSV file to upload.
- table: name of the table where the data will be inserted.

Example:

```bash
curl -X POST -F "file=@data/name_file.csv" -F "table=name_table" https://globantapi-565552294938.us-central1.run.app/uploadCSV
```


### 3. Backup a Table
This endpoint allows you to backup a table in AVRO format.

Endpoint: `POST /backup/<table_name>`

Example:

```bash
curl -X POST https://globantapi-565552294938.us-central1.run.app/backup/<table_name>
```

### 4. Restore a Table from Backup
This endpoint allows you to restore a table from a previously generated backup file.

Endpoint: `POST /restore/<table_name>`

Example:

```bash
curl -X POST https://globantapi-565552294938.us-central1.run.app/restore/<table_name>
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

### Manage Dockergile with Cloud Run
- upload docker file
```docker
docker build -t globantapi .
```

- run image docker
```docker
docker run -p 5000:5000 globantapi
```

- set docker
```docker
gcloud auth configure-docker
```

- Create tag docker
```docker
docker tag globantapi gcr.io/testeoz-2024/globantapi
```

- push tag docker to conteiner registry
```docker
docker push gcr.io/testeoz-2024/globantapi
```

## Deploy Cloud run

```bash
gcloud run deploy globantapi --image gcr.io/testeoz-2024/globantapi --platform managed --region us-central1 --allow-unauthenticated
```

## Important Note
This project uses mysql-connector-python instead of SQLAlchemy for database interaction. This decision was made due to complications encountered when installing SQLAlchemy on Ubuntu. By using mysql-connector-python, we saved time and avoided potential compatibility issues, while still maintaining an efficient way to handle database connections and queries.


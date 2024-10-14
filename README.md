# API
## CREATE TABLES AND DATA MODEL

```sql
CREATE TABLE departments (
    departament_id INT AUTO_INCREMENT PRIMARY KEY,
    departament_name VARCHAR(255) NOT NULL
);
```

```sql
CREATE TABLE jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    job_name VARCHAR(255) NOT NULL UNIQUE
);
```


```sql
CREATE TABLE hired_employed (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_name VARCHAR(255)  NULL,
    date_hired DATETIME  NULL,
    departament_id INT,
    job_id INT,
    CONSTRAINT fk_departament
        FOREIGN KEY (departament_id) REFERENCES departments(departament_id),
    CONSTRAINT fk_job
        FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);
```

## Endpoints Examples

### Endpoint para subir csv departaments

This endpoint allow upload file .CSV with detail where you insert data into table for can you have 
get register.

```bash
curl -X POST -F "file=@data/name_file.csv" -F "table=name_table" http://127.0.0.1:5000/uploadCSV
```
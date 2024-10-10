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
    employee_name VARCHAR(255) NOT NULL,
    date_hired DATETIME NOT NULL,
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
```bash
curl -X POST -F "file=@data/departments.csv" http://127.0.0.1:3000/uploadCSV
```
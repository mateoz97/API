# Usa una imagen base ligera de Python
FROM python:3.11-slim

# Instala Poetry
RUN pip install poetry

# Establece el directorio de trabajo
WORKDIR /API

# Copia el archivo pyproject.toml y poetry.lock
COPY pyproject.toml poetry.lock* /API/

# Instala las dependencias usando Poetry
RUN poetry config virtualenvs.create false && poetry install --no-dev

# Copia el código de la aplicación
COPY . .

# Expone el puerto 8080
EXPOSE 8080

# Define el comando de ejecución para la aplicación
CMD ["poetry", "run", "gunicorn", "-b", "0.0.0.0:8080", "app:app"]

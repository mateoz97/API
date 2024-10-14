FROM python:3.11

WORKDIR /usr/src/app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry

RUN poetry install --no-dev


COPY app ./app
COPY data ./data

EXPOSE 5000

CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0", "--port=8080"]

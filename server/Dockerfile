FROM python:3.9.0-slim

ADD . /code

RUN pip install poetry

WORKDIR /code

RUN poetry install

CMD ["poetry", "run", "gunicorn", "app:app", "-b", ":8080"]
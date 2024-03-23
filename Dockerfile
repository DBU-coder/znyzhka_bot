FROM python:3.12-alpine AS builder

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev --no-root

COPY src/ ./src

RUN poetry install --without dev

CMD ["poetry", "run", "python", "-m", "src.bot"]

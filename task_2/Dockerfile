FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./
RUN pip install --no-cache-dir poetry==2.2.1 \
    && poetry install --only main --no-root

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:voting_app", "--host", "0.0.0.0", "--port", "8000"]

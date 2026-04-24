FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN uv sync --system --no-dev

COPY . .

RUN mkdir -p /app/data

ENV DATABASE_URL=sqlite:////app/data/relay.db
ENV LOG_FILE=/app/data/relay.log

EXPOSE 8000

CMD ["python", "app.py"]

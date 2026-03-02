## Parent image — Python 3.12 slim (matches pyproject.toml requires-python)
FROM python:3.12-slim

## Essential environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

## Work directory inside the docker container
WORKDIR /app

## Installing system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

## Install uv — fast Python package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

## Copy dependency files first (better layer caching)
COPY pyproject.toml uv.lock .python-version ./

## Install dependencies using uv (without dev deps, frozen lockfile)
RUN uv sync --frozen --no-dev --no-install-project

## Add virtual environment to PATH (production optimization)
## - 'uv sync' creates a .venv in /app/.venv with all dependencies
## - By adding .venv/bin to PATH, installed binaries like 'python' resolve directly
## - This removes 'uv ' as a runtime dependency
ENV PATH="/app/.venv/bin:$PATH"

## Copy the rest of the project
COPY app/ app/
COPY data/ data/
COPY vectorstore/ vectorstore/
COPY main.py .

## Expose Flask port
EXPOSE 5000

## Run the Flask application
## - 'python' directly resolves to /app/.venv/bin/python (via PATH above)
## - No need for 'uv run' wrapper — the venv is already on PATH
CMD ["python", "-m", "app.application"]

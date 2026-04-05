FROM python:3.14-slim

# Get uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# App lives here
WORKDIR /app

# Use the virtualenv created by uv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Copy dependency metadata first for better layer caching
COPY pyproject.toml uv.lock .python-version ./

# Install only runtime dependencies from the lock file
RUN uv sync --locked --no-dev

# Copy application code
COPY src/ ./src/

# Run the pipeline
ENTRYPOINT ["python", "src/main.py"]
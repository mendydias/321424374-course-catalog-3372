FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 \
    TERM=xterm-256color

# Install production dependencies from the locked manifest first for layer caching.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# Copy application source.
COPY main.py ./
COPY models/ models/
COPY data/ data/
COPY controllers/ controllers/
COPY views/ views/

# Final locked sync picks up any project-local changes.
RUN uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"

# Run the TUI as PID 1; the container exits when the application exits.
CMD ["python", "main.py"]

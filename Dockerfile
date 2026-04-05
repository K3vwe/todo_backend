# ------------ Base Layer ------------
FROM python:3.14-slim-bookworm AS base
WORKDIR /app

# Create Non-user
RUN groupadd -r backend && useradd -r -g backend -m -s /bin/bash backend

# Virtual Environment
ENV VIRTUAL_ENV="/opt/venv"
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV PYTHONUNBUFFERED=1
# Python path
ENV PYTHONPATH=/app

# ------------ Builder Layer ------------
FROM base AS builder

COPY requirements.txt .

# Update system dependencies for packages that complie using c and c++ libraries
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip wheel \
    && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# ------------ Development Layer ------------
FROM base AS dev

ENV ENV=development

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

COPY --chown=backend:backend . .

USER backend

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# ------------ Test Layer ------------
FROM base AS test

ENV ENV=test

COPY --chown=backend:backend --from=builder /wheels /wheels

RUN pip install --no-index --no-cache-dir /wheels/* pytest

COPY --chown=backend:backend app /app/app

USER backend

CMD ["pytest", "-v"]

# ----------- Production Layer ------------
FROM base AS production

COPY --chown=backend:backend --from=builder /wheels /wheels

# Install tini for proper signal handling
RUN apt-get update && \
    apt-get install -y --no-install-recommends tini curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install wheels + gunicorn in production
RUN pip install --no-index --no-cache-dir /wheels/* 

COPY --chown=backend:backend app /app/app
COPY --chown=backend:backend alembic /app/alembic
COPY --chown=backend:backend alembic.ini /app/

USER backend

ENTRYPOINT ["/usr/bin/tini", "--"]

HEALTHCHECK --interval=30s --start-period=5s --retries=3 --timeout=10s \
    CMD curl http://localhost:8000/api/v1/health || exit 1

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000", "--workers", "3"]
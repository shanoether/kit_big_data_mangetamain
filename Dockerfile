# Minimal, reproducible Dockerfile using the slim Python image
# Installs project (reads pyproject.toml) instead of using requirements.txt

FROM python:3.12-slim

# Keep Python output unbuffered and avoid writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Minimal runtime system dependencies (keep image small). If a build is required
# for any package, you'll need to add build-essential and headers.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
       libfreetype6 \
       libpng16-16 \
    && rm -rf /var/lib/apt/lists/*

# Copy runtime requirements (a small subset of pyproject) and install
COPY requirements-runtime.txt /app/requirements-runtime.txt
#RUN python -m pip install --extra-index-url https://pypi.fury.io/arrow-nightlies/ \
#        --prefer-binary --pre pyarrow
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --prefer-binary --no-cache-dir -r /app/requirements-runtime.txt

# Copy source (only what's needed). Place package root under /app so
# `PYTHONPATH=/app` makes `import mangetamain` work without installing.
COPY src/ /app/

# Create mountpoint for processed data
RUN mkdir -p /app/data

# Make src importable (helpful if package not installed)
ENV PYTHONPATH=/app

# Default entrypoint runs the data processor module
ENTRYPOINT ["python", "-u", "-m", "mangetamain.backend.data_processor"]
CMD []

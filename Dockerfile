# # Multi-stage build for production-ready container
# FROM python:3.11-slim AS builder

# # Set environment variables
# ENV PYTHONUNBUFFERED=1 \
#     PYTHONDONTWRITEBYTECODE=1 \
#     PIP_NO_CACHE_DIR=1 \
#     PIP_DISABLE_PIP_VERSION_CHECK=1

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# # Install uv
# RUN pip install uv

# # Set work directory
# WORKDIR /app

# # Copy requirements first for better caching
# COPY pyproject.toml uv.lock README.md ./

# # Install Python dependencies
# RUN uv sync --frozen --no-dev

# # Copy source code
# COPY . .

# Production stage
FROM python:3.11-slim AS production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=".venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Create non-root user
# RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml uv.lock README.md ./

# Install Python dependencies
RUN uv sync --frozen --no-dev

# Copy source code
COPY . .

# # Copy virtual environment from builder stage
# COPY --from=builder /app/.venv /app/.venv

# # Copy application code
# COPY --from=builder /app/src /app/src

# # Change ownership to non-root user
# RUN chown -R appuser:appuser /app
# USER appuser

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/health || exit 1

# Run the application

# CMD ["ls", "-a"]
# CMD ["ls", ".venv/lib/python3.13/site-packages"]
CMD ["uv", "run", "streamlit", "run", "src/mangetamain/streamlit_ui.py", "--server.address=0.0.0.0", "--server.port=8501"]
# CMD ["streamlit", "run", "src/mangetamain/streamlit_ui.py", "--server.address=0.0.0.0", "--server.port=8501"]
# CMD ["uv", "pip", "show", "streamlit"]
# CMD ["ls", ".venv/lib/python3.11/site-packages"]
# CMD ["uv", "run", "/app/.venv/bin/streamlit", "run", "src/mangetamain/streamlit_ui.py", "--server.address=0.0.0.0", "--server.port=8501"]
# CMD ["ls", ".venv/bin"]
# CMD ["ls", "src/mangetamain"]
# CMD ["uv", "pip", "show", "streamlit"]
# ============================================================================
# Multi-stage Docker build for Vietnam Housing Price Prediction API
# Python 3.13.5 | Production-Ready | Optimized for Render/Railway
# ============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies
# -----------------------------------------------------------------------------
FROM python:3.13.5-slim AS builder

# Metadata
LABEL maintainer="CS106.TTNT Team"
LABEL description="Builder stage for Vietnam Housing Price API"

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies to user directory
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt


# -----------------------------------------------------------------------------
# Stage 2: Runtime - Final minimal image
# -----------------------------------------------------------------------------
FROM python:3.13.5-slim

# Metadata
LABEL maintainer="CS106.TTNT Team"
LABEL description="Vietnam Housing Price Prediction API - Production"
LABEL version="1.0"
LABEL python.version="3.13.5"

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy Python dependencies from builder stage
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Update PATH for user-installed packages
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application code with proper ownership
COPY --chown=appuser:appuser app/ /app/app/
COPY --chown=appuser:appuser models/ /app/models/
COPY --chown=appuser:appuser libs/ /app/libs/

# Set Python environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Default environment variables (can be overridden)
ENV PORT=8000 \
    LOG_LEVEL=INFO \
    DEBUG=False

# Switch to non-root user
USER appuser

# Expose port (Railway/Render will use PORT env var)
EXPOSE 8000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/api/v1/health || exit 1

# Run the application
# Use exec form to ensure proper signal handling
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]





Dockerfile

```dockerfile
# Dockerfile for Richard's Credit Authority

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
COPY pyproject.toml .

# Install dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Make scripts executable
RUN chmod +x cli.py

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Create necessary directories
RUN mkdir -p /home/appuser/.local/state/credit-authority \
    && chown appuser:appuser /home/appuser/.local/state/credit-authority

# Expose port (for future API)
EXPOSE 8000

# Default command
CMD ["python", "cli.py", "--help"]
```
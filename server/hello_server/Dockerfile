# Stage 1 - Builder
FROM python:3.12-slim as builder

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2 - Final
FROM gcr.io/distroless/python3-debian12

# Set working directory
WORKDIR /app

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY . /app

# Use nonroot user (distroless includes this user)
USER nonroot

# Expose port
EXPOSE 8000

# Run the application
ENTRYPOINT ["python", "hello-server.py"]

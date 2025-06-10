# Stage 1 - Builder
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --target /python-deps -r requirements.txt

# Stage 2 - Final
FROM gcr.io/distroless/python3-debian12

WORKDIR /app
ENV PYTHONPATH="/python-deps:/app"

COPY --from=builder /python-deps /python-deps
COPY . /app

USER nonroot
EXPOSE 8000
ENTRYPOINT ["python", "hello-server.py"]

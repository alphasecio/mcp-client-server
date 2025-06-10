# Stage 1 - Builder
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2 - Final
FROM gcr.io/distroless/python3-debian12

COPY --from=builder /install /usr/local
COPY . /app
WORKDIR /app

USER nonroot
EXPOSE 8000
ENTRYPOINT ["python", "hello-server.py"]

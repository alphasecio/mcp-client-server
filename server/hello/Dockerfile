# Stage 1 - Build
FROM cgr.dev/chainguard/python:latest-dev AS builder

WORKDIR /app

RUN uv venv venv
COPY requirements.txt .

RUN . venv/bin/activate && uv pip install --no-cache-dir -r requirements.txt

# Stage 2 - Run
FROM cgr.dev/chainguard/python:latest

WORKDIR /app

COPY --from=builder /app/venv /app/venv
COPY hello_server.py .

ENV PATH="/app/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

ENTRYPOINT ["python", "hello_server.py"]

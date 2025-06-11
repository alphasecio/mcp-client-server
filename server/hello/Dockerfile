# Stage 1 - Build
FROM cgr.dev/chainguard/python:latest-dev as build

USER root

WORKDIR /app
COPY requirements.txt .

# Install uv, then use it to install dependencies into /python-deps
RUN apk add --no-cache uv \
 && uv pip install --target=/python-deps --no-cache-dir -r requirements.txt

# Stage 2 - Run
FROM cgr.dev/chainguard/python:latest

USER nonroot

WORKDIR /app
COPY hello_server.py .
COPY --from=build /python-deps /python-deps

ENV PYTHONPATH="/python-deps"

ENTRYPOINT ["python", "hello_server.py"]

# Stage 1 - Build
FROM cgr.dev/chainguard/python:latest-dev as build

WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix=/python-deps --no-cache-dir -r requirements.txt

# Stage 2 - Run
FROM cgr.dev/chainguard/python:latest

WORKDIR /app
COPY hello-server.py .
COPY --from=build /python-deps /python-deps

ENV PYTHONPATH="/python-deps/lib/python3.11/site-packages"

ENTRYPOINT ["python", "hello-server.py"]

# Stage 1 - Build
FROM python:3.11-slim as build

WORKDIR /app
COPY requirements.txt .

RUN pip install --prefix=/python-deps --no-cache-dir -r requirements.txt

# Stage 2 - Run
FROM gcr.io/distroless/python3-debian12

WORKDIR /app
COPY --from=build /python-deps /python-deps
COPY web-risk-server.py .

ENV PYTHONPATH="/python-deps/lib/python3.11/site-packages"

USER nonroot
EXPOSE 8000

ENTRYPOINT ["python", "web-risk-server.py"]

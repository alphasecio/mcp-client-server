# Stage 1 - Build
FROM python:3.12-slim as build

WORKDIR /app
COPY requirements.txt .

RUN pip install --prefix=/python-deps --no-cache-dir -r requirements.txt

# Stage 2 - Run
FROM gcr.io/distroless/python3-debian12:nonroot

WORKDIR /app
COPY --from=build /python-deps /python-deps
COPY web_risk_server.py .

ENV PYTHONPATH="/python-deps/lib/python3.12/site-packages"

EXPOSE 8000

ENTRYPOINT ["python", "web_risk_server.py"]

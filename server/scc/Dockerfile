# Stage 1 — Build
FROM python:3.12-slim AS build

WORKDIR /app
COPY requirements.txt scc_mcp.py ./

RUN pip install --prefix=/python-deps --no-cache-dir -r requirements.txt

# Stage 2 — Run (Distroless)
FROM gcr.io/distroless/python3-debian12:nonroot

WORKDIR /app
COPY --from=build /python-deps /python-deps
COPY --from=build /app /app

ENV PYTHONPATH="/python-deps/lib/python3.12/site-packages"

EXPOSE 8080

ENTRYPOINT ["python", "scc_server.py"]

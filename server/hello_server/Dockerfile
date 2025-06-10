FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

USER nobody
EXPOSE 8000

ENTRYPOINT ["python", "hello-server.py"]

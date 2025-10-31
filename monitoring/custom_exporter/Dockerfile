FROM python:3.11-slim

WORKDIR /app
COPY custom_exporter.py /app/

RUN pip install --no-cache-dir prometheus_client requests

CMD ["python", "custom_exporter.py"]

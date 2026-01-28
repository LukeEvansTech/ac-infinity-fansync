FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

USER 65534:65534

ENTRYPOINT ["python", "-m", "src.main"]

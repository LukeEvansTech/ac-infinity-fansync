FROM python:3.14-slim@sha256:f85c5697265c178cc6887276c55fe16cf3d14ca35c3df6a5eab3b360534a55d2

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

USER 65534:65534

# Long-running fan controller — health-check by importing the entrypoint
# module (it loads the runtime config and validates env on import).
HEALTHCHECK --interval=60s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import src.main" || exit 1

ENTRYPOINT ["python", "-m", "src.main"]

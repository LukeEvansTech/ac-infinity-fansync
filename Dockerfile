FROM python:3.15-slim@sha256:8c13a3f37a6a5b71498228e902c4b9f51c1f7900d49fabf71f9a650c6120e0d0

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

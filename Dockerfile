FROM python:3.15-slim@sha256:533b0b2f9b5d46fd097091cf826f27902f1d6c3bca714b6dc74551356aa97a51

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

FROM python:3.12-slim@sha256:57cd7c3a7a273101a6485ba99423ee568157882804b1124b4dd04266317710de AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/src

RUN groupadd --system app && useradd --system --gid app --create-home app
WORKDIR /app

COPY requirements/runtime.txt ./requirements/runtime.txt
RUN python -m pip install --require-hashes -r requirements/runtime.txt && python -m pip check

COPY pyproject.toml README.md ./
COPY src ./src

RUN mkdir -p /app/artifacts && chown -R app:app /app
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

CMD ["python", "-m", "uvicorn", "four_pillars.api:app", "--host", "0.0.0.0", "--port", "8000"]

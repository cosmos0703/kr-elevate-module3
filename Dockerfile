FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

COPY pyproject.toml /app/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    google-adk \
    google-cloud-discoveryengine \
    google-cloud-storage \
    python-dotenv \
    pyyaml \
    pypdf \
    fastmcp \
    httpx

COPY . /app/

EXPOSE 8080

CMD ["python", "-m", "agent.fast_api_app"]

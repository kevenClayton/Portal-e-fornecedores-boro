# Imagem oficial Playwright (Python + Chromium)
FROM mcr.microsoft.com/playwright/python:v1.49.1-jammy

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    HEADLESS=true \
    USAR_CHROME_SISTEMA=false \
    DOCKER=true

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY run.py .
COPY src ./src

# Logs persistentes via volume
RUN mkdir -p /app/logs

CMD ["python", "run.py"]

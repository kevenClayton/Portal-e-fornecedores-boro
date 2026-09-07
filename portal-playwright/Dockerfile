# Imagem oficial Playwright (Python) + Google Chrome real
# O portal Usiminas rejeita Chromium/Playwright na checagem de "Sites Confiáveis".
FROM mcr.microsoft.com/playwright/python:v1.61.0-jammy

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    HEADLESS=false \
    USAR_CHROME_SISTEMA=true \
    DOCKER=true \
    DISPLAY=:99

RUN apt-get update \
    && apt-get install -y --no-install-recommends xvfb wget gnupg \
    && wget -qO- https://dl.google.com/linux/linux_signing_key.pub \
      | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
      > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY run.py .
COPY src ./src
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

RUN mkdir -p /app/logs

ENTRYPOINT ["/docker-entrypoint.sh"]

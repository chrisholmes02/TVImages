FROM python:3.12-slim

# Install system dependencies Playwright/Chromium needs
RUN apt-get update && apt-get install -y \
    wget curl gnupg ca-certificates \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libasound2 libpango-1.0-0 libpangocairo-1.0-0 \
    libgtk-3-0 libx11-xcb1 libxcb-dri3-0 \
    && rm -rf /var/lib/apt/lists/*

# Pin playwright so the Python package and browser binary always match
RUN pip install --no-cache-dir "playwright==1.49.0" requests

# Install Chromium + all its system dependencies in one step
# --with-deps ensures no version mismatch between the library and browser
RUN playwright install --with-deps chromium

WORKDIR /app
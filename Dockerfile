FROM python:3.12-slim

# Install all system libraries Chromium requires
RUN apt-get update && apt-get install -y \
    wget curl gnupg ca-certificates \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libpango-1.0-0 libpangocairo-1.0-0 \
    libgtk-3-0 libx11-xcb1 libxcb-dri3-0 \
    libx11-6 libxcb1 libxext6 libxss1 \
    libglib2.0-0 libasound2 fonts-liberation \
    dbus dbus-x11 \
    && rm -rf /var/lib/apt/lists/*

# Pin playwright so the Python package and browser binary always match
RUN pip install --no-cache-dir "playwright==1.49.0" requests

# Install Chromium browser only (no --with-deps, we handled deps above)
RUN playwright install chromium

WORKDIR /app
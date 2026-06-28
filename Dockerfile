# Official Playwright image — comes with Chromium and all dependencies pre-installed
FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

# Install requests (everything else is already in the base image)
RUN pip install --no-cache-dir requests

WORKDIR /app
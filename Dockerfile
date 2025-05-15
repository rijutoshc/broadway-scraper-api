FROM python:3.11-slim

# Install system dependencies for Playwright Chromium
RUN apt-get update && apt-get install -y \
    wget curl unzip \
    libnss3 libatk-bridge2.0-0 libgtk-3-0 libxss1 libasound2 libgbm-dev libu2f-udev \
    fonts-liberation libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxrandr2 \
    libdrm2 libxfixes3 libxi6 libgl1 libgl1-mesa-glx && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install --with-deps

EXPOSE 5000
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:5000"]

FROM python:3.10-slim

# Install Chrome and dependencies
RUN apt-get update && \
    apt-get install -y wget gnupg2 unzip curl xvfb libnss3 libgconf-2-4 libxss1 libappindicator1 fonts-liberation libasound2 libnspr4 libx11-xcb1 libxcb-dri3-0 libxcomposite1 libxcursor1 libxdamage1 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["gunicorn", "server:app", "--bind", "0.0.0.0:${PORT}", "--workers", "1", "--timeout", "0"]

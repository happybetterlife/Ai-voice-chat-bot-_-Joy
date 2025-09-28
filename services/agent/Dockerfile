FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /tmp/requirements.txt
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r /tmp/requirements.txt
COPY services/agent /app
CMD ["python","worker.py"]

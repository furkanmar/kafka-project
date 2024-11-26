FROM python:3.9-slim

# PostgreSQL geliştirme araçları ve bağımlılıkları yükleniyor
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY producer.py producer.py

CMD ["python", "producer.py"]

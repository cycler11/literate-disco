FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Создаем директорию для загрузок
RUN mkdir -p /app/uploads
RUN chmod 777 /app/uploads

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Установка Bootstrap Icons
RUN mkdir -p /app/static/bootstrap-icons
RUN wget https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css -P /app/static/bootstrap-icons/
RUN wget https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/fonts/bootstrap-icons.woff2 -P /app/static/bootstrap-icons/fonts/

COPY . .

EXPOSE 5000

CMD ["python", "run.py"]

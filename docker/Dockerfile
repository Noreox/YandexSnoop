FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY YandexSnoop.py .
COPY .env .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "YandexSnoop.py"]
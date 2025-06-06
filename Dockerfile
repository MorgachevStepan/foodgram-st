FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential libpq-dev libjpeg-dev zlib1g-dev gettext curl postgresql-client \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY backend/ .

COPY ./data /app/data

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]
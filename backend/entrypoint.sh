#!/bin/sh

set -e

echo "Waiting for PostgreSQL..."

export PGPASSWORD=$POSTGRES_PASSWORD

while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER" -q; do
  echo "PostgreSQL is unavailable - sleeping (Host: $DB_HOST, Port: $DB_PORT, User: $POSTGRES_USER)"
  sleep 1
done

echo "PostgreSQL started"


echo "Applying database migrations..."

python manage.py migrate --noinput

echo "Collecting static files..."

python manage.py collectstatic --noinput --clear

echo "Loading ingredients..."

python manage.py load_ingredients

echo "Starting Gunicorn server..."
exec "$@"
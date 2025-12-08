#!/usr/bin/env sh
set -e

# Wait for Postgres
if [ -n "$DATABASE_URL" ]; then
  echo "Waiting for database..."
  until nc -z "${POSTGRES_HOST:-db}" "${POSTGRES_PORT:-5432}"; do
    sleep 1
  done
fi

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Copy admin static to ensure availability when using volume bind mounts
cp -r /app/staticfiles/admin /app/static 2>/dev/null || true

echo "Starting Gunicorn..."
exec gunicorn library_system.wsgi:application --bind 0.0.0.0:8000



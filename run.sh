#!/usr/bin/env sh
set -e

# Ensure Python deps are installed
if [ -f "requirements.txt" ]; then
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
fi

# Collect static files
python manage.py collectstatic --noinput

# Apply migrations
python manage.py migrate --noinput

# Start the server
python manage.py runserver 0.0.0.0:8000



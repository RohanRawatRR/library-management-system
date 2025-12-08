## Library Management (Django + DRF)

Features:
- User roles: anonymous (browse), members (borrow), admins (manage books/users).
- JWT auth (login, refresh), registration endpoints.
- Books search/browse, borrow/return flows; loan history for authenticated users.
- Admin site plus frontend pages (home, login, signup).
- Docker support (PostgreSQL), WhiteNoise static serving, DRF-YASG API docs.

### Requirements
- Python 3.12+
- (Optional) Docker & Docker Compose

### Environment
Copy `env.example` to `.env` and adjust:
```
SECRET_KEY=your-secret
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://library_user:library_pass@db:5432/library_db
POSTGRES_DB=library_db
POSTGRES_USER=library_user
POSTGRES_PASSWORD=library_pass
POSTGRES_HOST=db
POSTGRES_PORT=5432
DB_HOST_PORT=5433
```
For local SQLite dev, you can omit `DATABASE_URL`.

### Run locally (no Docker)
```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```
Visit http://localhost:8000/ (frontend), http://localhost:8000/admin/, swagger at http://localhost:8000/swagger/ and Redoc at http://localhost:8000/redoc/.

### Run via Docker
```sh
chmod +x run_docker.sh
./run_docker.sh
```
Containers start in the background; entrypoint handles migrations & collectstatic. App on http://localhost:8000.

### API Docs
- Swagger UI: `/swagger/`
- Redoc: `/redoc/`
- JSON/YAML: `/swagger.json`, `/swagger.yaml`

### Frontend filters/search (Books)
- Search by title/author/ISBN via the search box.
- Availability filter (available/not available).
- Pagination (prev/next) with total count shown; filters persist across pages.

### Helpful scripts
- `run.sh` — installs deps, runs migrations & collectstatic, starts dev server.
- `run_docker.sh` — builds/starts Docker stack, migrations handled in entrypoint.

### Admin
Create a superuser if needed:
```sh
python manage.py createsuperuser
```

### Deployment notes (Heroku/others)
- `Procfile` provided (`release` runs migrations, `web` runs gunicorn).
- `runtime.txt` pins Python version.
- Ensure env vars: `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `DATABASE_URL`.
- Static files served via WhiteNoise (uses `STATIC_ROOT=staticfiles`; run `collectstatic`).



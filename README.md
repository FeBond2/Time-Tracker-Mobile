# Time Tracker

- **Mobile app:** React Native/Expo app in the `mobile/` subfolder.
- **Backend:** Django API in the `backend/` subfolder. All backend commands below are run from `backend/` (e.g. `cd backend` first).

## Backend (Django) — run from `backend/`

- **Python 3.10+** recommended. From `backend/`: create a venv and install: `pip install -r requirements.txt`
- **Migrations:** `python manage.py migrate`
- **Superuser (admin portal):** `python manage.py createsuperuser`
- **Run server:** `python manage.py runserver` → API at `http://127.0.0.1:8000/api/`, Admin at `http://127.0.0.1:8000/admin/`

## API

- Auth: `POST /api/auth/register/`, `POST /api/auth/login/` (username + password → JWT), `POST /api/auth/token/refresh/`, `GET /api/auth/me/`
- Entries: `GET/POST /api/entries/`, `GET/PATCH/DELETE /api/entries/<id>/`
- Categories: `GET/POST /api/categories/`, `GET/PATCH/DELETE /api/categories/<id>/`
- PTO: `GET/POST /api/pto/`, `GET/PATCH/DELETE /api/pto/<id>/`, `GET /api/pto/summary/?year=YYYY`
- Settings: `GET /api/settings/pto-policy/?year=YYYY`

Use header: `Authorization: Bearer <access_token>` for protected endpoints.

## Import / Export

- **Import backup (API):** `POST /api/import-backup/` with JSON body: `{ "entries": [...], "pto": { "entries": [...] } }`. Same shape as the legacy app export. Deduplicates by (date, description, timePeriods) for entries.
- **Export backup (API):** `GET /api/export-backup/` returns JSON with `entries`, `pto`, `exportDate`, `version` for the current user.
- **Import backup (CLI):** `python manage.py import_backup path/to/backup.json --username myuser`

## Production

- Copy `.env.example` to `.env` and set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`, `DJANGO_ALLOWED_HOSTS`, and `CORS_ORIGINS` (comma-separated origins that the mobile app or web frontend use).
- Run with a production WSGI server (e.g. Gunicorn) and put a reverse proxy (e.g. Nginx) in front with HTTPS.
- For the mobile app, the device must reach your API over HTTPS; set the app’s API URL to your backend base URL (see this README).

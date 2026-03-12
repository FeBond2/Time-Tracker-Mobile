# Vercel serverless entry: expose Django WSGI app as `app`
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

# Run migrations at runtime (Vercel build often doesn't have DB env vars; runtime does).
# Safe to run on every cold start: migrate is idempotent.
call_command("migrate", "--noinput")

app = get_wsgi_application()

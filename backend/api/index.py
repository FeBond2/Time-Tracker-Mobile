# Vercel serverless entry: expose Django WSGI app as `app`
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()  # Required before call_command or get_wsgi_application

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

# Run migrations at runtime (Vercel has DB env at runtime). Don't crash the function if it fails.
try:
    call_command("migrate", "--noinput")
except Exception as e:
    print(f"[api/index] migrate failed: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)

app = get_wsgi_application()

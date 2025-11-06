#!/bin/sh
set -e

echo "[entrypoint] Running Django setup..."

# collect staticfiles and migrate db
python manage.py collectstatic --noinput
python manage.py migrate

# create user (guest & admin)
python manage.py shell <<'PYCODE'
import os
from django.contrib.auth import get_user_model

User = get_user_model()

# ---- Superuser ----
admin_email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
admin_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpassword')
admin_fullname = os.environ.get('DJANGO_SUPERUSER_FULLNAME', 'Admin User')

if not User.objects.filter(email=admin_email).exists():
    print(f"[entrypoint] Creating superuser '{admin_email}' ...")
    User.objects.create_superuser(email=admin_email, password=admin_password, fullname=admin_fullname)
    print(f"[entrypoint] Superuser '{admin_email}' created.")
else:
    print(f"[entrypoint] Superuser '{admin_email}' already exists.")

# ---- Guest User ----
guest_email = os.environ.get('DJANGO_GUEST_EMAIL', 'guest@videoflix.com')
guest_password = os.environ.get('DJANGO_GUEST_PASSWORD', 'guestpassword')
guest_fullname = os.environ.get('DJANGO_GUEST_FULLNAME', 'Guest User')

if not User.objects.filter(email=guest_email).exists():
    print(f"[entrypoint] Creating guest user '{guest_email}' ...")
    guest = User.objects.create_user(email=guest_email, password=guest_password, fullname=guest_fullname)
    guest.is_staff = False
    guest.is_superuser = False
    guest.save()
    print(f"[entrypoint] Guest user '{guest_email}' created.")
else:
    print(f"[entrypoint] Guest user '{guest_email}' already exists.")
PYCODE

# ---- run Gunicorn ----
echo "[entrypoint] Starting Gunicorn..."
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000

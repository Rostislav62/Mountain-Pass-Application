# /Mountain Pass Application/create_superuser.py

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User

# Проверяем, существует ли уже суперпользователь
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "AdminPassword123")
    print("✅ Суперпользователь создан: admin / AdminPassword123")
else:
    print("ℹ️ Суперпользователь уже существует.")

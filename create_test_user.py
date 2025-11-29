#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'irongate.settings')
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', '', 'admin123')
    print('✅ Admin user created: admin / admin123')
else:
    print('✅ Admin user already exists')

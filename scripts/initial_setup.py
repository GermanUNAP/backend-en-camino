import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'encamino.settings')
django.setup()

User = get_user_model()

def create_superuser():
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@latamstore.com',
            password='admin123',
            role='admin'
        )
        print("Superuser 'admin' creado con password 'admin123'")
    else:
        print("Superuser ya existe")

if __name__ == "__main__":
    create_superuser()
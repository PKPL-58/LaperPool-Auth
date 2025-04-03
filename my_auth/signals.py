import os
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from dotenv import load_dotenv
from my_auth.models import Admin, Manager

# Load environment variables from .env file
load_dotenv()
# Get the user model
User = get_user_model()

@receiver(post_migrate)
def create_superuser(sender, **kwargs):
    username = os.getenv("PODS_DJANGO_SUPERUSER_USERNAME", "admin@gmail.com")
    email = os.getenv("PODS_DJANGO_SUPERUSER_EMAIL", "admin@gmail.com")
    password = os.getenv("PODS_DJANGO_SUPERUSER_PASSWORD", "Admin12345.")

    if not Admin.objects.filter(username=username).exists():
        print(f"[SIGNAL] Creating default superuser '{username}'...")
        Admin.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            phone_number="1234567890",
            role=User.ADMIN,
        )
    else:
        print(f"[SIGNAL] Superuser '{username}' already exists. Skipping.")

@receiver(post_migrate)
def create_manager(sender, **kwargs):
    username = os.getenv("PODS_DJANGO_MANAGER_USERNAME", "manager@gmail.com")
    email = os.getenv("PODS_DJANGO_MANAGER_EMAIL", "manager@gmail.com")
    password = os.getenv("PODS_DJANGO_MANAGER_PASSWORD", "Manager12345.")

    if not Manager.objects.filter(username=username).exists():
        print(f"[SIGNAL] Creating default manager '{username}'...")
        Manager.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            phone_number="2345678901",
            role=User.MANAGER,
        )
    else:
        print(f"[SIGNAL] Manager '{username}' already exists. Skipping.")
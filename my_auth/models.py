from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
import re

# Membuat model user yang mewarisi AbstractUser
class MyUser(AbstractUser):
    phone_number = models.CharField(unique=True, max_length=15)

    def clean_nomor_hp(self):
        if not re.match(r'^\d{8,15}$', self.nomor_hp):
            raise ValidationError("Nomor HP harus memiliki panjang antara 8 dan 15 digit angka.")

    def __str__(self):
        return self.username
    

    # Solve conflict between AbstractUser and MyUser
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='myuser_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='myuser_permission_set',
        blank=True
    )

class Customer(MyUser):
    hashed_pin = models.BinaryField()
    alamat = models.TextField()
    saldo = models.IntegerField(default=0)

    def clean_alamat(self):
        self.alamat = re.sub(r'[^a-zA-Z0-9\s]', '', self.alamat)

    def __str__(self):
        return self.username

class Manager(MyUser):
    def __str__(self):
        return self.username
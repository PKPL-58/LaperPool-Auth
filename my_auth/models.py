from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
import re

class MyUser(AbstractUser):
    CUSTOMER = 'customer'
    MANAGER = 'manager'
    ROLE_CHOICES = [
        (CUSTOMER, 'Customer'),
        (MANAGER, 'Manager'),
    ]
    

    phone_number = models.CharField(unique=True, max_length=15)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=CUSTOMER
    )

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
    
    def save(self, *args, **kwargs):
        self.role = self.MANAGER
        super().save(*args, **kwargs)
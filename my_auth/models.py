from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
import re

class MyUser(AbstractUser):
    CUSTOMER = 'customer'
    MANAGER = 'manager'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (CUSTOMER, 'Customer'),
        (MANAGER, 'Manager'),
        (ADMIN, 'Admin'),
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

    class Meta:
        verbose_name = "MyUser"
        verbose_name_plural = "MyUsers"

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

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        self.role = self.CUSTOMER
        super().save(*args, **kwargs)

        customer_group, created = Group.objects.get_or_create(name='Customer')
        self.groups.add(customer_group)

class Manager(MyUser):

    class Meta:
        verbose_name = "Manager"
        verbose_name_plural = "Managers"

    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        self.role = self.MANAGER
        super().save(*args, **kwargs)

        manager_group, created = Group.objects.get_or_create(name='Manager')
        self.groups.add(manager_group)

class Admin(MyUser):

    class Meta:
        verbose_name = "Admin"
        verbose_name_plural = "Admins"

    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        self.role = self.ADMIN
        super().save(*args, **kwargs)
    
        admin_group, created = Group.objects.get_or_create(name='Admin')
        self.groups.add(admin_group)
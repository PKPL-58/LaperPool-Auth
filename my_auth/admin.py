from django.contrib import admin
from .models import MyUser, Customer, Manager, Admin

# Register your models here.

@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    search_fields = ('username', 'email')         

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('username', 'alamat', 'saldo')
    search_fields = ('username', 'alamat')

@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    search_fields = ('username', 'email')

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('username', 'email') 
    search_fields = ('username', 'email')
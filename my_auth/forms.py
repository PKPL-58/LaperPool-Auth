from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils.html import escape
from django import forms
from .models import Customer
import bcrypt

class CustomerCreationForm(UserCreationForm):
    pin = forms.CharField(
        label='PIN',
        widget=forms.PasswordInput,
        validators=[
            RegexValidator(
                regex=r'^\d{6}$',  # Validasi 6 digit angka
                message='PIN harus berupa 6 digit angka.',
            )
        ]
    )
    
    class Meta:
        model = Customer
        fields = ('username', 'phone_number', 'password1', 'password2', 'alamat', 'pin')
        widgets = {
            'alamat': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        email_validator = EmailValidator(message="Masukkan email yang valid.")
        email_validator(username)
        return username

    def clean_alamat(self):
        alamat = self.cleaned_data.get('alamat', '').strip()
        return escape(alamat)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number', '').strip()
        if not phone_number.isdigit():
            raise ValidationError("Nomor telepon hanya boleh mengandung angka.")
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.hashed_pin = bcrypt.hashpw(self.cleaned_data["pin"].encode(), bcrypt.gensalt())
        if commit:
            user.save()
        return user
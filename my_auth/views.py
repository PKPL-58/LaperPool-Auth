from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomerCreationForm
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponseRedirect
from django.conf import settings
from my_auth.utils import login_ratelimit
from laperpool_auth.constant import HOME_URL
from django.urls import reverse
from rest_framework_simplejwt.authentication import JWTAuthentication
from laperpool_auth import settings


def index(request):
    return redirect('auth:login')

def register(request):
    if request.method == 'POST':
        print(request.POST)
        form = CustomerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Akun berhasil dibuat! Silakan login.')
            return redirect('auth:login')
        else:
            messages.error(request, 'Terdapat kesalahan pada form. Periksa kembali data yang dimasukkan.')
    else:
        form = CustomerCreationForm()

    return render(request, 'register.html', {'form': form})

@login_ratelimit(key='post:username', rate='5/m', method='POST', block=True)
def login(request):
    if is_authenticate(request):
        return redirect(HOME_URL)

    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response = HttpResponseRedirect(HOME_URL)
            
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=access_token,
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                path='/',
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
            )

            print("Login berhasil dengan username: ", request.POST['username'])
            return response
        else:
            messages.error(request, 'Username atau password salah.')
            print("Login gagal dengan username: ", request.POST['username'])
            return redirect('auth:login')
        
    else:
        return render(request, 'login.html')

def logout(request):
    response = HttpResponseRedirect(reverse('auth:login'))
    response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
    request.session.flush() 
    return response

# Function Helper untuk cek apakah sudah terautentikasi
def is_authenticate(request):
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])

        if raw_token is None:
            return False
        
        try:
            auth = JWTAuthentication()
            validated_token = auth.get_validated_token(raw_token)
            print("Token valid")
            return True
        except Exception as e:
            print(e)
            print("Token tidak valid")
            return False
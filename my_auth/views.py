from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomerCreationForm
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from .models import MyUser
from django.http import HttpResponseRedirect
from django.conf import settings

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

def login(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response = HttpResponseRedirect('http://localhost:8000/')  # Ganti dengan URL tujuan
            
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
    response = JsonResponse({
        'message': 'Logout berhasil!'
    })
    response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
    request.session.flush() 
    return response
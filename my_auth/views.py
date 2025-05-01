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
import logging

logger = logging.getLogger(__name__)

def index(request):
    return redirect('auth:login')

def register(request):
    if request.method == 'POST':
        logger.info("Menerima permintaan POST untuk registrasi.")
        logger.debug(f"Data POST: {request.POST}")
        
        form = CustomerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            logger.info(f"Registrasi berhasil untuk pengguna: {form.cleaned_data.get('username')}")
            messages.success(request, 'Akun berhasil dibuat! Silakan login.')
            return redirect('auth:login')
        else:
            logger.warning("Registrasi gagal. Form tidak valid.")
            logger.debug(f"Kesalahan pada form: {form.errors}")
            messages.error(request, 'Terdapat kesalahan pada form. Periksa kembali data yang dimasukkan.')
    else:
        logger.info("Menerima permintaan GET untuk halaman registrasi.")
        form = CustomerCreationForm()

    return render(request, 'register.html', {'form': form})

@login_ratelimit(rate='5/m', method='POST', block=True)
def login(request):
    if is_authenticate(request):
        logger.info("Pengguna sudah terautentikasi, mengarahkan ke HOME_URL.")
        return redirect(HOME_URL)

    if request.method == 'POST':
        logger.info("Menerima permintaan POST untuk login.")

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, 'Username dan password tidak boleh kosong.')
            return redirect('auth:login')

        if not is_valid_username(username):
            messages.error(request, 'Username hanya boleh mengandung huruf, angka, underscore, @, dan titik.')
            return redirect('auth:login')

        if len(username) < 3 or len(username) > 150:
            messages.error(request, 'Username harus memiliki panjang antara 3 hingga 150 karakter.')
            return redirect('auth:login')

        if len(password) < 8:
            messages.error(request, 'Password harus memiliki panjang minimal 8 karakter.')
            return redirect('auth:login')

        # Proses autentikasi
        user = authenticate(username=username, password=password)
        
        if user is not None:
            logger.info(f"Login berhasil untuk pengguna: {user.username}")
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response = HttpResponseRedirect(HOME_URL)
            
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=access_token,
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                domain='.pkpl.cs.ui.ac.id',
                path='/',
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
            )

            logger.debug(f"Cookie JWT berhasil disetel untuk pengguna: {user.username}")
            return response
        else:
            logger.warning("Login gagal. Username atau password salah.")
            messages.error(request, 'Username atau password salah.')
            return redirect('auth:login')
        
    else:
        logger.info("Menerima permintaan GET untuk halaman login.")
        return render(request, 'login.html')

def logout(request):
    logger.info("Pengguna melakukan logout.")
    
    response = HttpResponseRedirect(reverse('auth:login'))
    
    response.delete_cookie(
        key=settings.SIMPLE_JWT['AUTH_COOKIE'],
        domain='.pkpl.cs.ui.ac.id',
        path='/'
    )    

    logger.debug("Cookie JWT berhasil dihapus.")
    request.session.flush()
    logger.debug("Session pengguna berhasil dihapus.")
    
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

# Function Helper untuk validasi username
def is_valid_username(username):
    import re
    pattern = r'^[a-zA-Z0-9_.@]+$'
    return re.match(pattern, username) is not None
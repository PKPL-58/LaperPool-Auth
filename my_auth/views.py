from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomerCreationForm

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
    return render(request, 'login.html')

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from .utils import generate_password
from .models import *
from django.contrib import messages
from .forms import *

def sign_up(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.instance.username = generate_password()
            form.instance.role = 'owner'
            form.save()
            return redirect('dashboard')
    return render(request, 'user/sign_up.html', {'form': form})


def login_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Вы вошли в систему')
            return redirect('dashboard')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    return render(request, 'user/login.html')


def logout_user(request):
    logout(request)
    return redirect('login')

@login_required
def list(request):
    users = User.objects.filter(shop=request.user.shop)

    if request.method == 'POST' and 'delete' in request.POST:
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return redirect('user-list')
        
    return render(request, 'user/list.html', {'users': users})

@login_required
def create(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.instance.shop = request.user.shop
            form.save()
            return redirect('users_list')

    context = {
        'form':form
    }
    return render(request, 'user/create.html', context)

@login_required
def profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserProfileForm(instance=user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {
        'user': user,
        'form': form
    }
    return render(request, 'user/profile.html', context)
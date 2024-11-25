from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from .forms import *


def login_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Вы вошли в систему')
            return redirect('dashboard')
               
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, 'user/login.html')


def logout_user(request):
    logout(request)
    return redirect('schedule')


def list(request):
    users = User.objects.filter(shop=request.user.shop)

    if request.method == 'POST' and 'delete' in request.POST:
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return redirect('user-list')
        
    return render(request, 'user/list.html', {'users': users})





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


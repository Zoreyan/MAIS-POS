from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from apps.utils.utils import generate_text, check_permission
from django.db.models import Q
from apps.dashboard.models import *
from .models import *
from .forms import *
from apps.utils.utils import delete_obj
from apps.history.models import LogHistory

def login_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.has_access:
            login(request, user)
            LogHistory.objects.create(user=request.user, message='Вошел в систему', object=request.user.username)
            messages.success(request, 'Вы вошли в систему')
            return redirect('dashboard')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    return render(request, 'user/login.html')

@login_required
def logout_user(request):
    logout(request)
    return redirect('login')


@check_permission
@login_required
def list(request):
    users = User.objects.filter(shop=request.user.shop)

    role = request.GET.get('role')
    if role and role != 'all':
        users = users.filter(role=role)

    search_query = request.GET.get('search', '')
    if search_query:    
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(phone__icontains=search_query)  # Предполагается, что телефон хранится в связанном профиле
        )
    context = {
        'users': users,
        'search_query': search_query,
        'selected_role': role,
    }
    return render(request, 'user/list.html', context)


@login_required
@check_permission
def profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserProfileForm(instance=user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = user.role
            LogHistory.objects.create(user=request.user, message='Обновлен пользователь', object=user.username)
            user.save()
            return redirect('user-profile', pk=user.id)

    
    context = {
        'user': user,
        'form': form
    }
    return render(request, 'user/profile.html', context)



@login_required
@check_permission
def create(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST, request.FILES)
        if form.is_valid():
            login_password = generate_text()
            User.objects.create_user(
                password=login_password, username=login_password, shop=request.user.shop,
                first_name=form.cleaned_data['first_name'], last_name=form.cleaned_data['last_name'],
                phone=form.cleaned_data['phone'], email=form.cleaned_data['email'],
                image=form.files['image'], role=form.cleaned_data['role'])
            LogHistory.objects.create(user=request.user, message='Создан пользователь', object=form.cleaned_data['username'])
            messages.success(request, 'Пользователь успешно создан.')
            return redirect('user-list')
    context = {'form': form}
    return render(request, 'user/create.html', context)

@login_required
@check_permission
def delete(request, pk):
    delete_obj(request, User, pk, 'Удален пользователь')
    return redirect('user-list')

def notifications(request, pk):
    user = get_object_or_404(User, pk=pk)
    notifications = Notification.objects.filter(shop=user.shop).order_by('-created')
    
    unread_ids = [n.id for n in notifications if user in n.is_not_read.all()]
    
    for notification in notifications:
        if user in notification.is_not_read.all():
            notification.is_not_read.remove(user)
            notification.save()

    return render(request, 'user/notifications.html', {
        'notifications': notifications,
        'unread_ids': unread_ids
    })
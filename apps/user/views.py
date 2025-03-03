from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.models import Permission
from django.http import JsonResponse
from django.db.utils import IntegrityError
from django.contrib import messages
from .utils import generate_text, check_permission
from django.db.models import Q
from apps.dashboard.models import *
from .models import *
from .forms import *



def login_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.has_access:
            login(request, user)
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

            messages.success(request, 'Пользователь успешно создан.')
            return redirect('user-list')
    context = {'form': form}
    return render(request, 'user/create.html', context)

@login_required
@check_permission
def delete(request, pk):
    permission = Permission.objects.filter(user=request.user, codename='delete_user')
    if not permission.exists():
        referer = request.META.get('HTTP_REFERER')  # Получить URL предыдущей страницы
        if referer:  # Если заголовок HTTP_REFERER доступен
            return redirect(referer)
        return redirect('dashboard')

    user = User.objects.get(id=pk)
    user.delete()
    return redirect('user-list')

@login_required
@check_permission
def notifications(request, pk):

    user = get_object_or_404(User, pk=pk)
    notifications = Notification.objects.filter(shop=user.shop).order_by('-created')
    for notification in notifications:
        if user in notification.is_not_read.all():
            notification.is_not_read.remove(user)

    return render(request, 'user/notifications.html', {'notifications': notifications})
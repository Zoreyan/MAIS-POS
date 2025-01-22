from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.models import Permission
from django.http import JsonResponse
from django.db.utils import IntegrityError
from django.contrib import messages
from django.db.models import Q

from .utils import generate_password
from .models import *
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
    # Получение всех пользователей
    users = User.objects.filter(shop=request.user.shop)

    # Обработка фильтрации по роли
    role = request.GET.get('role')
    if role and role != 'all':  # Убедитесь, что роль указана и не равна "все"
        users = users.filter(role=role)

    search_query = request.GET.get('search', '')
    if search_query:    
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)  # Предполагается, что телефон хранится в связанном профиле
        )

    return render(request, 'user/list.html', {
        'users': users,
        'search_query': search_query,
        'selected_role': role,
    })


@login_required
def profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    user_permissions = Permission.objects.filter(user=user)
    form = UserProfileForm(instance=user)


    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = user.role  # Сохранение старого значения роли
            user.save()
            return redirect('user-profile', pk=user.id)

    
    permissions_data = {
        'can_create_user': user_permissions.filter(codename='add_user').exists(),
        'can_delete_user': user_permissions.filter(codename='delete_user').exists(),
        'can_edit_user': user_permissions.filter(codename='change_user').exists(),
        'can_view_user': user_permissions.filter(codename='view_user').exists(),
        
        'can_create_product': user_permissions.filter(codename='add_product').exists(),
        'can_delete_product': user_permissions.filter(codename='delete_product').exists(),
        'can_edit_product': user_permissions.filter(codename='change_product').exists(),
        'can_view_product': user_permissions.filter(codename='view_product').exists(),
        
        'can_create_category': user_permissions.filter(codename='add_category').exists(),
        'can_delete_category': user_permissions.filter(codename='delete_category').exists(),
        'can_edit_category': user_permissions.filter(codename='change_category').exists(),
        'can_view_category': user_permissions.filter(codename='view_category').exists(),
        
        'can_create_expense': user_permissions.filter(codename='add_expense').exists(),
        'can_delete_expense': user_permissions.filter(codename='delete_expense').exists(),
        'can_edit_expense': user_permissions.filter(codename='change_expense').exists(),
        'can_view_expense': user_permissions.filter(codename='view_expense').exists(),
        
        'can_delete_orderhistory': user_permissions.filter(codename='delete_orderhistory').exists(),
        'can_view_orderhistory': user_permissions.filter(codename='view_orderhistory').exists(),
        
        'can_delete_soldhistory': user_permissions.filter(codename='delete_soldhistory').exists(),
        'can_view_soldhistory': user_permissions.filter(codename='view_soldhistory').exists(),
        
        'can_delete_incomehistory': user_permissions.filter(codename='delete_incomehistory').exists(),
        'can_view_incomehistory': user_permissions.filter(codename='view_incomehistory').exists(),
    }

    context = {
        'user': user,
        'permissions': permissions_data,
        'form': form
    }
    return render(request, 'user/profile.html', context)



@login_required
def create(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            try:
                # Создаём пользователя
                new_user = form.save(commit=False)
                new_user.shop = request.user.shop
                new_user.role = form.cleaned_data['role']
                new_user.save()

                # Список прав для обработки
                permissions_mapping = {
                    # Пользователь
                    'can_create_user': 'add_user',
                    'can_delete_user': 'delete_user',
                    'can_edit_user': 'change_user',
                    'can_view_user': 'view_user',
                    # Товар
                    'can_create_product': 'add_product',
                    'can_delete_product': 'delete_product',
                    'can_edit_product': 'change_product',
                    'can_view_product': 'view_product',
                    # Категория
                    'can_create_category': 'add_category',
                    'can_delete_category': 'delete_category',
                    'can_edit_category': 'change_category',
                    'can_view_category': 'view_category',
                    # Расход
                    'can_create_expense': 'add_expense',
                    'can_delete_expense': 'delete_expense',
                    'can_edit_expense': 'change_expense',
                    'can_view_expense': 'view_expense',
                    # Общая история
                    'can_delete_orderhistory': 'delete_orderhistory',
                    'can_view_orderhistory': 'view_orderhistory',
                    # История продаж
                    'can_delete_soldhistory': 'delete_soldhistory',
                    'can_view_soldhistory': 'view_soldhistory',
                    # История поставок
                    'can_delete_incomehistory': 'delete_incomehistory',
                    'can_view_incomehistory': 'view_incomehistory',
                }

                # Устанавливаем права
                for checkbox_name, permission_codename in permissions_mapping.items():
                    if request.POST.get(checkbox_name) == 'on':
                        try:
                            permission = Permission.objects.get(codename=permission_codename)
                            new_user.user_permissions.add(permission)
                        except Permission.DoesNotExist:
                            # Логгируем, если право не найдено
                            print(f"Permission '{permission_codename}' not found.")

                new_user.save()
                messages.success(request, 'Пользователь успешно создан.')
                return redirect('user-list')

            except IntegrityError as e:
                if 'UNIQUE constraint failed' in str(e):
                    messages.error(request, 'Пользователь с таким email уже существует.')
                else:
                    messages.error(request, 'Произошла ошибка при сохранении пользователя.')
        
    context = {'form': form}
    return render(request, 'user/create.html', context)

ROLE_PERMISSIONS = {
    'admin': {
        'can_create_user': True,
        'can_delete_user': True,
        'can_edit_user': True,
        'can_view_user': True,
        'can_create_product': True,
        'can_delete_product': True,
        'can_edit_product': True,
        'can_view_product': True,
        'can_create_category': True,
        'can_delete_category': True,
        'can_edit_category': True,
        'can_view_category': True,
        'can_create_expense': True,
        'can_delete_expense': True,
        'can_edit_expense': True,
        'can_view_expense': True,
        'can_delete_orderhistory': True,
        'can_view_orderhistory': True,
        'can_delete_soldhistory': True,
        'can_view_soldhistory': True,
        'can_delete_incomehistory': True,
        'can_view_incomehistory': True,
    },
    'manager': {
        'can_create_user': False,
        'can_delete_user': False,
        'can_edit_user': True,
        'can_view_user': True,
        'can_create_product': True,
        'can_delete_product': True,
        'can_edit_product': True,
        'can_view_product': True,
        'can_create_category': True,
        'can_delete_category': False,
        'can_edit_category': True,
        'can_view_category': True,
        'can_create_expense': True,
        'can_delete_expense': False,
        'can_edit_expense': True,
        'can_view_expense': True,
        'can_delete_orderhistory': False,
        'can_view_orderhistory': True,
        'can_delete_soldhistory': False,
        'can_view_soldhistory': True,
        'can_delete_incomehistory': False,
        'can_view_incomehistory': True,
    },
    'cashier': {
        'can_create_user': False,
        'can_delete_user': False,
        'can_edit_user': False,
        'can_view_user': True,
        'can_create_product': False,
        'can_delete_product': False,
        'can_edit_product': False,
        'can_view_product': True,
        'can_create_category': False,
        'can_delete_category': False,
        'can_edit_category': False,
        'can_view_category': True,
        'can_create_expense': False,
        'can_delete_expense': False,
        'can_edit_expense': False,
        'can_view_expense': True,
        'can_delete_orderhistory': False,
        'can_view_orderhistory': True,
        'can_delete_soldhistory': False,
        'can_view_soldhistory': True,
        'can_delete_incomehistory': False,
        'can_view_incomehistory': True,
    },
    'owner': {
        'can_create_user': True,
        'can_delete_user': True,
        'can_edit_user': True,
        'can_view_user': True,
        'can_create_product': True,
        'can_delete_product': True,
        'can_edit_product': True,
        'can_view_product': True,
        'can_create_category': True,
        'can_delete_category': True,
        'can_edit_category': True,
        'can_view_category': True,
        'can_create_expense': True,
        'can_delete_expense': True,
        'can_edit_expense': True,
        'can_view_expense': True,
        'can_delete_orderhistory': True,
        'can_view_orderhistory': True,
        'can_delete_soldhistory': True,
        'can_view_soldhistory': True,
        'can_delete_incomehistory': True,
        'can_view_incomehistory': True,
    },
}

@login_required
def get_permissions(request):
    role = request.GET.get('role')
    permissions = ROLE_PERMISSIONS.get(role, {})

    return JsonResponse(permissions)

def get_user_permissions(request):
    user_id = request.GET.get('user_id')
    user = get_object_or_404(User, id=user_id)
    
    # Получаем все права пользователя
    user_permissions = Permission.objects.filter(user=user)
    
    # Формируем словарь с правами
    permissions_data = {
        'can_create_user': user_permissions.filter(codename='add_user').exists(),
        'can_delete_user': user_permissions.filter(codename='delete_user').exists(),
        'can_edit_user': user_permissions.filter(codename='change_user').exists(),
        'can_view_user': user_permissions.filter(codename='view_user').exists(),
        
        'can_create_product': user_permissions.filter(codename='add_product').exists(),
        'can_delete_product': user_permissions.filter(codename='delete_product').exists(),
        'can_edit_product': user_permissions.filter(codename='change_product').exists(),
        'can_view_product': user_permissions.filter(codename='view_product').exists(),
        
        'can_create_category': user_permissions.filter(codename='add_category').exists(),
        'can_delete_category': user_permissions.filter(codename='delete_category').exists(),
        'can_edit_category': user_permissions.filter(codename='change_category').exists(),
        'can_view_category': user_permissions.filter(codename='view_category').exists(),
        
        'can_create_expense': user_permissions.filter(codename='add_expense').exists(),
        'can_delete_expense': user_permissions.filter(codename='delete_expense').exists(),
        'can_edit_expense': user_permissions.filter(codename='change_expense').exists(),
        'can_view_expense': user_permissions.filter(codename='view_expense').exists(),
        
        'can_delete_orderhistory': user_permissions.filter(codename='delete_orderhistory').exists(),
        'can_view_orderhistory': user_permissions.filter(codename='view_orderhistory').exists(),
        
        'can_delete_soldhistory': user_permissions.filter(codename='delete_soldhistory').exists(),
        'can_view_soldhistory': user_permissions.filter(codename='view_soldhistory').exists(),
        
        'can_delete_incomehistory': user_permissions.filter(codename='delete_incomehistory').exists(),
        'can_view_incomehistory': user_permissions.filter(codename='view_incomehistory').exists(),
    }
    
    return JsonResponse(permissions_data)


def update(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserUpdateForm(request.POST or None, request.FILES or None, instance=user)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            try:
                # Создаём пользователя
                new_user = form.save(commit=False)
                new_user.shop = request.user.shop
                new_user.role = form.cleaned_data['role']
                new_user.save()

                # Список прав для обработки
                permissions_mapping = {
                    # Пользователь
                    'can_create_user': 'add_user',
                    'can_delete_user': 'delete_user',
                    'can_edit_user': 'change_user',
                    'can_view_user': 'view_user',
                    # Товар
                    'can_create_product': 'add_product',
                    'can_delete_product': 'delete_product',
                    'can_edit_product': 'change_product',
                    'can_view_product': 'view_product',
                    # Категория
                    'can_create_category': 'add_category',
                    'can_delete_category': 'delete_category',
                    'can_edit_category': 'change_category',
                    'can_view_category': 'view_category',
                    # Расход
                    'can_create_expense': 'add_expense',
                    'can_delete_expense': 'delete_expense',
                    'can_edit_expense': 'change_expense',
                    'can_view_expense': 'view_expense',
                    # Общая история
                    'can_delete_orderhistory': 'delete_orderhistory',
                    'can_view_orderhistory': 'view_orderhistory',
                    # История продаж
                    'can_delete_soldhistory': 'delete_soldhistory',
                    'can_view_soldhistory': 'view_soldhistory',
                    # История поставок
                    'can_delete_incomehistory': 'delete_incomehistory',
                    'can_view_incomehistory': 'view_incomehistory',
                }

                new_user.user_permissions.clear()
                for checkbox_name, permission_codename in permissions_mapping.items():
                    if request.POST.get(checkbox_name) == 'on':
                        try:
                            permission = Permission.objects.get(codename=permission_codename)
                            new_user.user_permissions.add(permission)
                        except Permission.DoesNotExist:
                            # Логгируем, если право не найдено
                            print(f"Permission '{permission_codename}' not found.")

                new_user.save()
                messages.success(request, 'Пользователь успешно создан.')
                return redirect('user-list')

            except IntegrityError as e:
                if 'UNIQUE constraint failed' in str(e):
                    messages.error(request, 'Пользователь с таким email уже существует.')
                else:
                    messages.error(request, 'Произошла ошибка при сохранении пользователя.')

    context = {
        'user': user,
        'form':form
    }
    return render(request, 'user/update.html', context)

def delete(request, pk):
    user = User.objects.get(id=pk)
    user.delete()
    return redirect('user-list')
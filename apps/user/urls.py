from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path
from .views import *


urlpatterns = [
    path('list/', list, name='user-list'),
    path('create/', create, name='user-create'),
    path('login/', login_page, name='login'),
    path('logout/', logout_user, name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
]
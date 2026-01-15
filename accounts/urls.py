from django.urls import path
from . import views
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [

    path('password_reset/', views.request_password_reset, name='request_password_reset'),
    path('password_reset/verify/', views.verify_pin, name='verify_pin'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('profile/', views.profile_view, name='profile'),
    path('password_change/', views.password_change_view, name='password_change'),

]
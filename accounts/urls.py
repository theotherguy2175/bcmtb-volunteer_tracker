from django.urls import path
from . import views
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views

urlpatterns = [

    path('password_reset/', views.request_password_reset, name='request_password_reset'),
    path('password_reset/verify/', views.verify_pin, name='verify_pin'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # path('accounts/password-reset/', views.MyPasswordResetView.as_view(), name='password_reset'),
    # re_path(
    #     r'^accounts/reset/(?P<uidb64>[^/]+)/(?P<token>[^/]+)/$', 
    #     views.MyCustomPasswordResetConfirmView.as_view(), 
    #     name='password_reset_confirm'
    # ),
]
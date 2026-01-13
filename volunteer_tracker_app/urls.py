"""
URL configuration for volunteer_tracker_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from . import views

from django.views.static import serve
from django.views.generic.base import RedirectView

from django.conf import settings
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path




urlpatterns = [
    path('accounts/login/', views.CustomLoginView.as_view(), name='login'),

    path('accounts/password-reset/', views.MyPasswordResetView.as_view(), name='password_reset'),
    re_path(
        r'^accounts/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 
        auth_views.PasswordResetConfirmView.as_view(), 
        name='password_reset_confirm'
    ),
    #path('accounts/reset/<uidb64>/<token>/', views.MyCustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('profile/', views.profile_view, name='profile'),
    path('password_change/', views.password_change_view, name='password_change'),


    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'images/bcmb_logo.ico')),
    path('admin/', admin.site.urls),
    path('', include('hourTracker.urls')),  # main app
    path('accounts/', include('django.contrib.auth.urls')),  # login/logout
    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]


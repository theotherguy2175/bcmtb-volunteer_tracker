from django.urls import path, include
from . import views

urlpatterns = [
    # path('login/', views.login_view, name='login'),

    path('', views.dashboard, name='dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add/', views.add_entry, name='add_entry'),
    path('edit/<int:pk>/', views.edit_entry, name='edit_entry'),
    path('delete/<int:pk>/', views.delete_entry, name='delete_entry'),

    path('register/', views.register_view, name='register'),
    path('rewards/', views.rewards, name='rewards'),

    path('export-csv/', views.export_csv, name='export_csv'),
]


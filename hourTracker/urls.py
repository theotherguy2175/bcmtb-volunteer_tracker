from django.urls import path, re_path
from . import views


urlpatterns = [

    path('', views.dashboard, name='dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add/', views.add_entry, name='add_entry'),
    path('admin_add/', views.admin_add_entry, name='admin_add_entry'),
    path('edit/<int:pk>/', views.edit_entry, name='edit_entry'),
    path('delete/<int:pk>/', views.delete_entry, name='delete_entry'),

    path('register/', views.register_view, name='register'),
    path('activate/<str:uidb64>/<path:token>/', views.activate, name='activate'),
    path('resend-activation/', views.resend_activation, name='resend_activation'),

    path('rewards/', views.rewards, name='rewards'),

    path('export-csv/', views.export_csv, name='export_csv'),

    path('reports/', views.reports_page, name='reports'),
    path('reports/export-entries/', views.export_volunteer_entries_csv, name='export_entries'),
    path('reports/export-users/', views.export_users_csv, name='export_users'),
    path('reports/export-yearly-totals/', views.export_user_yearly_totals_csv, name='export_yearly_totals'),

]


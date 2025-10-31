from django.contrib import admin
from .models import VolunteerEntry

@admin.register(VolunteerEntry)
class VolunteerEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'hours', 'category')
    list_filter = ('category',)
    search_fields = ('user__username',)

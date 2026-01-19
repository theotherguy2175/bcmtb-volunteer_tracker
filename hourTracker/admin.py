from django.contrib import admin
from .models import CustomUser, VolunteerEntry, VolunteerTask
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, VolunteerEntry, VolunteerLocation, VolunteerReward

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from .forms import CustomUserCreationForm  # Ensure this import is correct

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from .forms import CustomUserCreationForm

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    # 1. Link your custom creation form
    add_form = CustomUserCreationForm

    # 2. Add address fields to the list view table
    # Added city and state here so you can sort/see them at a glance
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'city', 'state', 'is_staff', 'is_active')

    # Added city and state to filters for easier volunteer management
    list_filter = ('is_staff', 'is_active', 'state', 'city')

    # 3. Update Edit View (fieldsets)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number')}),
        (_('Address Details'), {'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'zip_code')}), # New Section
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # 4. Update Creation View (add_fieldsets)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 
                'first_name', 
                'last_name', 
                'phone_number', 
                'address_line_1',
                'address_line_2',
                'city',
                'state',
                'zip_code',
                'password1', 
                'password2', 
                'is_staff', 
                'is_active'
            )
        }),
    )

    # Expanded search to include city and zip
    search_fields = ('email', 'first_name', 'last_name', 'phone_number', 'city', 'zip_code')
    ordering = ('email',)


# @admin.register(VolunteerEntry)
# class VolunteerEntryAdmin(admin.ModelAdmin):
#     list_display = ("user", "date", "hours", "category")

@admin.register(VolunteerTask)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(VolunteerEntry)
class VolunteerEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'hours', 'category')
    list_filter = ('category', 'date')
    search_fields = ('user__email',)

@admin.register(VolunteerLocation)
class VolunteerLocationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(VolunteerReward)
class RewardAdmin(admin.ModelAdmin):
    # This makes the admin list view show the name and the hours required
    list_display = ('name', 'hours_required')
    # This allows you to click the name to edit the reward
    list_display_links = ('name',)


# hourTracker/admin.py
from django.contrib import admin
from .models import RewardSettings

@admin.register(RewardSettings)
class RewardSettingsAdmin(admin.ModelAdmin):
    # This prevents the admin from adding more than one settings object
    def has_add_permission(self, request):
        return not RewardSettings.objects.exists()
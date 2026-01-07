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

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    # 1. Link your custom creation form
    add_form = CustomUserCreationForm

    # 2. Add phone_number to the list view table
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'is_staff', 'is_active')

    list_filter = ('is_staff', 'is_active')

    # 3. Update Edit View (fieldsets)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number')}), # Added here
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # 4. Update Creation View (add_fieldsets)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 
                'phone_number', 
                'first_name', 
                'last_name', 
                'password1', 
                'password2', 
                'is_staff', 
                'is_active'
            )
        }),
    )

    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
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
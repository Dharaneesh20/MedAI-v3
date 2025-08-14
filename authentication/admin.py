from django.contrib import admin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'date_of_birth', 'phone_number')}),
        ('Emergency Contact', {'fields': ('emergency_contact', 'emergency_phone')}),
        ('Medical Information', {'fields': ('allergies', 'chronic_conditions', 'current_medications', 'medical_notes')}),
        ('Profile', {'fields': ('profile_picture',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'share_medical_history', 'receive_notifications', 'preferred_language')
    list_filter = ('share_medical_history', 'receive_notifications', 'preferred_language')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

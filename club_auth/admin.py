# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['studentId', 'name', 'role', 'email', 'year', 'semester']
    fieldsets = (
        (None, {'fields': ('studentId', 'password')}),
        ('Personal Info', {'fields': ('name', 'role', 'email', 'bio', 'avatar')}),
        ('Academic Info', {'fields': ('year', 'semester', 'interests', 'skills')}),
        ('Social Links', {'fields': ('github', 'linkedin')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('studentId', 'password1', 'password2', 'email', 'is_staff', 'is_active'),
        }),
    )
    search_fields = ['studentId', 'name', 'email']
    ordering = ['studentId']

admin.site.register(CustomUser, CustomUserAdmin)

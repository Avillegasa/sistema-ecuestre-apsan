# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, JudgeProfile

class JudgeProfileInline(admin.StackedInline):
    model = JudgeProfile
    can_delete = False
    verbose_name_plural = 'Perfil de Juez'

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff', 'is_judge')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name')}),
        ('Permisos', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Información de Juez', {'fields': ('is_judge', 'judge_level', 'judge_license')}),
        ('Fechas', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')}
        ),
    )
    
    inlines = [JudgeProfileInline]

# Registrar modelos en admin
admin.site.register(User, CustomUserAdmin)


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


# competitions/admin.py
from django.contrib import admin
from .models import (
    Competition, Category, CompetitionCategory, 
    CompetitionJudge, Rider, Horse, Participant
)

class CompetitionCategoryInline(admin.TabularInline):
    model = CompetitionCategory
    extra = 1

class CompetitionJudgeInline(admin.TabularInline):
    model = CompetitionJudge
    extra = 3
    max_num = 3

class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 1

@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'is_public', 'start_date')
    search_fields = ('name', 'location')
    date_hierarchy = 'start_date'
    
    inlines = [CompetitionCategoryInline, CompetitionJudgeInline, ParticipantInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'min_age', 'max_age')
    search_fields = ('name', 'code')

@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'nationality', 'birth_date')
    list_filter = ('nationality',)
    search_fields = ('first_name', 'last_name')

@admin.register(Horse)
class HorseAdmin(admin.ModelAdmin):
    list_display = ('name', 'breed', 'birth_year', 'color')
    list_filter = ('breed', 'gender')
    search_fields = ('name', 'registration_number', 'microchip')

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('competition', 'rider', 'horse', 'number', 'order', 'is_withdrawn')
    list_filter = ('competition', 'category', 'is_withdrawn')
    search_fields = ('rider__first_name', 'rider__last_name', 'horse__name')
    autocomplete_fields = ['rider', 'horse']


# judging/admin.py
from django.contrib import admin
from .models import (
    EvaluationParameter, CompetitionParameter, Score, ScoreEdit, 
    Ranking, FirebaseSync, OfflineData
)

@admin.register(EvaluationParameter)
class EvaluationParameterAdmin(admin.ModelAdmin):
    list_display = ('name', 'coefficient', 'max_value')
    search_fields = ('name',)

class CompetitionParameterAdmin(admin.ModelAdmin):
    list_display = ('competition', 'parameter', 'order', 'effective_coefficient', 'effective_max_value')
    list_filter = ('competition',)
    autocomplete_fields = ['competition', 'parameter']

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('judge', 'participant', 'parameter', 'value', 'calculated_result', 'is_edited')
    list_filter = ('competition', 'judge', 'is_edited')
    search_fields = ('participant__rider__first_name', 'participant__rider__last_name', 'participant__horse__name')
    date_hierarchy = 'created_at'
    autocomplete_fields = ['judge', 'participant', 'parameter']

@admin.register(ScoreEdit)
class ScoreEditAdmin(admin.ModelAdmin):
    list_display = ('score', 'editor', 'previous_value', 'previous_result', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('score__participant__rider__first_name', 'score__participant__rider__last_name')
    date_hierarchy = 'created_at'
    readonly_fields = ('score', 'editor', 'previous_value', 'previous_result', 'created_at')

@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ('competition', 'participant', 'position', 'average_score', 'percentage')
    list_filter = ('competition',)
    search_fields = ('participant__rider__first_name', 'participant__rider__last_name', 'participant__horse__name')
    ordering = ('competition', 'position')
    autocomplete_fields = ['competition', 'participant']

@admin.register(FirebaseSync)
class FirebaseSyncAdmin(admin.ModelAdmin):
    list_display = ('competition', 'last_sync', 'is_synced')
    list_filter = ('is_synced',)
    search_fields = ('competition__name',)
    date_hierarchy = 'last_sync'
    readonly_fields = ('competition', 'last_sync', 'is_synced', 'error_message', 'created_at')

@admin.register(OfflineData)
class OfflineDataAdmin(admin.ModelAdmin):
    list_display = ('judge', 'competition', 'is_synced', 'sync_attempts', 'created_at')
    list_filter = ('is_synced', 'competition')
    search_fields = ('judge__first_name', 'judge__last_name', 'competition__name')
    date_hierarchy = 'created_at'
    autocomplete_fields = ['judge', 'competition', 'participant']

# Registrar CompetitionParameter
admin.site.register(CompetitionParameter, CompetitionParameterAdmin)
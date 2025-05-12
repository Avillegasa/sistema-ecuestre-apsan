
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
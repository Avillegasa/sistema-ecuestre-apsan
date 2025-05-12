
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


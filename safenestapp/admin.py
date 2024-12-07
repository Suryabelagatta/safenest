from django.contrib import admin
from .models import MissingChild, FoundChild, Statistics

@admin.register(MissingChild)
class MissingChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'last_seen_location', 'date_reported')
    search_fields = ('name', 'parent__username', 'last_seen_location')

@admin.register(FoundChild)
class FoundChildAdmin(admin.ModelAdmin):
    list_display = ('reporter_name', 'found_location', 'found_date', 'date_reported')
    search_fields = ('reporter_name', 'found_location')

@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'children_found')

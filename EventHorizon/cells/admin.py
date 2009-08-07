from django.contrib import admin
from cells.models import *


class ProcessingCycleOptions(admin.ModelAdmin):
    list_display = ('id', 'status', 'last_update',)
    list_filter = ('status',)
    date_hierarchy = 'last_update'
    

class SocietyCellOptions(admin.ModelAdmin):
    list_display = ('name', 'core', 'layer', 'location', 'container', 'child_count', 'external_id', 'last_processing_cycle', 'last_processing_time',)
    list_filter = ('layer', 'last_processing_cycle',)
    search_fields = ('name', 'core', 'location',)
    ordering = ('name',)
    

class AgentCellOptions(admin.ModelAdmin):
    list_display = ('name', 'core', 'layer', 'location', 'container', 'child_count', 'external_id', 'last_story_fetched_at', 'last_summary_delivered_at', 'last_processing_cycle', 'last_processing_time',)
    list_filter = ('layer', 'last_processing_cycle',)
    search_fields = ('name', 'core', 'location',)
    ordering = ('name',)


class StoryCellOptions(admin.ModelAdmin):
    list_display = ('name', 'core', 'layer', 'location', 'container', 'x', 'y', 'child_count', 'external_id', 'is_aggregation', 'last_processing_cycle', 'last_processing_time',)
    list_filter = ('layer', 'last_processing_cycle', 'is_aggregation')
    search_fields = ('name', 'core', 'location',)
    ordering = ('name',)


class UserCellOptions(admin.ModelAdmin):
    list_display = ('name', 'core', 'layer', 'location', 'container', 'child_count', 'external_id', 'last_processing_cycle', 'last_processing_time',)
    list_filter = ('layer', 'last_processing_cycle',)
    search_fields = ('name', 'core', 'location',)
    ordering = ('name',)
    

class ConceptCellOptions(admin.ModelAdmin):
    list_display = ('name', 'core', 'layer', 'location', 'container', 'child_count', 'external_id', 'last_processing_cycle', 'last_processing_time',)
    list_filter = ('layer', 'last_processing_cycle',)
    search_fields = ('name', 'core', 'location',)
    ordering = ('name',)
    

    

admin.site.register(ProcessingCycle, ProcessingCycleOptions)
admin.site.register(SocietyCell, SocietyCellOptions)
admin.site.register(AgentCell, AgentCellOptions)
admin.site.register(StoryCell, StoryCellOptions)
admin.site.register(UserCell, UserCellOptions)
admin.site.register(ConceptCell, ConceptCellOptions)

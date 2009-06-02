from django.contrib import admin
from cells.models import *


class SocietyCellOptions(admin.ModelAdmin):
    list_display = ('name', 'core', 'layer', 'x', 'y', 'container', 'child_count', 'external_id', 'last_processing_cycle', 'last_processing_time',)
    list_filter = ('layer', 'last_processing_cycle',)
    search_fields = ('name', 'core')
    ordering = ('name',)
    

class AgentCellOptions(admin.ModelAdmin):
    list_display = ('name', 'core', 'layer', 'x', 'y', 'container', 'child_count', 'external_id', 'last_processing_cycle', 'last_processing_time',)
    list_filter = ('layer', 'last_processing_cycle',)
    search_fields = ('name', 'core')
    ordering = ('name',)


class StoryCellOptions(admin.ModelAdmin):
    list_display = ('name', 'core', 'layer', 'x', 'y', 'container', 'child_count', 'external_id', 'last_processing_cycle', 'last_processing_time',)
    list_filter = ('layer', 'last_processing_cycle',)
    search_fields = ('name', 'core')
    ordering = ('name',)


class UserCellOptions(admin.ModelAdmin):
    list_display = ('name', 'core', 'layer', 'x', 'y', 'container', 'child_count', 'external_id', 'last_processing_cycle', 'last_processing_time',)
    list_filter = ('layer', 'last_processing_cycle',)
    search_fields = ('name', 'core')
    ordering = ('name',)

    

    
admin.site.register(SocietyCell, SocietyCellOptions)
admin.site.register(AgentCell, AgentCellOptions)
admin.site.register(StoryCell, StoryCellOptions)
admin.site.register(UserCell, UserCellOptions)

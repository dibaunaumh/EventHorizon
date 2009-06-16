from django.contrib import admin
from models import *


class EventTypeOptions(admin.ModelAdmin):
    list_display = ('name', 'description',)
    search_fields = ('name', 'description',)
    ordering = ('name',)


class EventLogOptions(admin.ModelAdmin):
    list_display = ('event_type', 'entity_type', 'entity_id', 'message', 'correlation_id', 'last_update',)
    list_filter = ('event_type', 'entity_type',)
    search_fields = ('event_type__name', 'entity_type', 'entity_id', 'message', 'correlation_id',)
    date_hierarchy = 'last_update'
    ordering = ('-last_update',)
    
    
admin.site.register(EventType, EventTypeOptions)
admin.site.register(EventLog, EventLogOptions)
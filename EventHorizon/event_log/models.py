from django.db import models
from django.utils.translation import gettext_lazy as _
import logging


class EventType(models.Model):
    """A type of system event, to be logged"""
    name = models.CharField(_('name'), db_index=True, unique=True, max_length=500)
    description = models.CharField(_('description'), max_length=5000, null=True, blank=True)
    last_update = models.DateTimeField(_('last update'), auto_now=True)
    
    
    def __unicode__(self):
        return self.name
    
    

class EventLog(models.Model):
    """Represents some system event"""
    event_type = models.ForeignKey(EventType, db_index=True, verbose_name=_('event type'))
    entity_type = models.CharField(_('entity type'), null=True, blank=True, max_length=500, db_index=True, help_text=_('The type of the entity subject of this event'))
    entity_id = models.IntegerField(_('entity id'), null=True, blank=True, db_index=True, help_text=_('The id of the entity subject of this event'))
    message = models.CharField(_('message'), null=True, blank=True, max_length=5000, help_text=_('Describes the event details'))
    correlation_id = models.CharField(_('correlation id'), null=True, blank=True, max_length=1000, db_index=True, help_text=_('An identifier used to correlate different events, which together compose some flow'))
    last_update = models.DateTimeField(_('last update'), auto_now=True)
    
    
    #def __init__(self, event_type, entity_type, entity_id, message=None, correlation_id=None):
    #    self.event_type = event_type
    #    self.entity_type = entity_type
    #    self.entity_id = entity_id
    #    self.message = message
    #    self.correlation_id = correlation_id
        
    
    def __unicode__(self):
        return u"%s %s: %s" % (event_type, _('event'), message)
    
    

def log_event(event_type_name, entity_type, entity_id, message=None, correlation_id=None):
    """Logs an event, by creating an EventLog object, saving & returning it."""
    query = EventType.objects.filter(name=event_type_name)
    if query.count() > 0:
        event_type = query[0]
        log = EventLog()
        log.event_type = event_type
        log.entity_type = entity_type
        log.entity_id = entity_id
        log.message = message
        log.correlation_id = correlation_id
        log.save()
        return log
    else:
        logging.error("Can't log event: wrong event type given: %s" % event_type_name)
        return None
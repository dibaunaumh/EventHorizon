"""
Test cases for the Event Log app.
"""

from django.test import TestCase
from event_log.models import *
import datetime

class SimpleTest(TestCase):
    
    def test_log_event(self):
        """
        Tests the log_event method
        """
        event_type_name = "TestEventType"
        query = EventType.objects.filter(name=event_type_name)
        if query.count() > 0:
            event_type = query[0]
        else:
            event_type = EventType()
            event_type.name = event_type_name
            event_type.save()
        d = datetime.datetime.now().microsecond
        message = "Test event.%d" % d
        entity_type = "SocietyCell"
        entity_id = 1
        log = log_event(event_type_name, entity_type, entity_id, message)
        query = EventLog.objects.filter(message=message)
        self.assertEqual(1, query.count(), "Couldn't find event log")
        event_log = query[0]
        self.assertEqual(event_type_name, event_log.event_type.name)
        self.assertEqual(entity_type, event_log.entity_type)
        self.assertEqual(entity_id, event_log.entity_id)
        

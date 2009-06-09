"""
Test cases for the cells app.
"""

from django.test import TestCase
from django.contrib.sites.models import *
from cells.models import *
from event_log.models import *
import datetime
import sys
from django.test import Client
from django.core.urlresolvers import reverse


class CellsTest(TestCase):
    
    
    def setUp(self):
        query = SocietyCell.objects.all()
        if query.count() > 0:
            self.society_cell = query[0]
        else:
            self.society_cell = SocietyCell()
            self.society_cell.name = "Test domain"
            self.society_cell.layer = 0
            self.society_cell.core = "A test society"
            self.society_cell.move_to_random_location()
    
    
    def test_move_to_random_location(self):
        # try many times
        for i in range(100):
            self.assertTrue(self.society_cell.move_to_random_location() != None)
    
    
    def test_move_to(self):
        agent1 = self.society_cell.add_agent("test1", "test1", DATASOURCE_TYPE_TWITTER)
        loc = (666, 777)
        agent1.move_to(loc)
        self.failUnlessEqual(agent1.get_location(), loc, "Location not set properly by move_to")
        agent2 = self.society_cell.add_agent("test2", "test2", DATASOURCE_TYPE_TWITTER)
        agent1.move_to_random_location()
        loc = agent1.get_location()
        self.failUnlessRaises(LocationCaughtError,  agent2.move_to, loc)
                         

    def test_location(self):
        agent3 = self.society_cell.add_agent("test3", "test3", DATASOURCE_TYPE_TWITTER)
        agent3.move_to_random_location()
        expected = "(layer-%d, %d, %d)" % (agent3.layer, agent3.x, agent3.y)
        self.failUnlessEqual(expected, agent3.location, "Location property not as expected") 


    def test_add_user(self):
        # todo implement
        pass
    
    
    def test_fetch_stories(self):
        # todo implement
        pass
    
    
    def test_processing(self):
        d = datetime.datetime.now().microsecond
        self.society_cell.process(d)
        query = EventLog.objects.filter(correlation_id=d)
        self.assertTrue(query.count > 3)
        
    
    def test_process_service(self):
        """Tests that invoking the process service indeed results in processing events. Requires a running server"""
        client = Client()
        # todo use reverse
        response = client.get("/cells/process/1")
        log = response.context[-1]['log']
        print log
        # todo extract the processing cycle id, & get the log of events for that id
        self.failUnless(len(log) > 3, "Processing log has too few events")
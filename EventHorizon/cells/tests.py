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
    
    
    
    def test_summary_generation(self):
    	"""Creates 3 users: 
    	   - Joe
    	   - Chris
    	   - Alice
    	   Creates 5 stories: 
    		- Story 1: by Joe, read by Chris
    		- Story 2: by Chris, read by Joe
    		- Story 3: by Chris, read by Joe
    		- Story 4: by Chris, read by Joe
    		- Story 5: by Alice, read by Joe
    		Invokes cells processing.
    		Expects to find 2 summary stories from today:
    		- Summary for Joe, containing the number of stories by Chris (3) & Alice (1)
    		- Summary for Chris, containing the number of stories by Joe (1)
    		"""
    	# add agents
    	self.society_cell.add_agent("Joe", "Joe", DATASOURCE_TYPE_TWITTER)
    	self.society_cell.add_agent("Chris", "Chris", DATASOURCE_TYPE_TWITTER)
    	self.society_cell.add_agent("Alice", "Alice", DATASOURCE_TYPE_TWITTER)
    	# fetch agents
    	query = AgentCell.objects.filter(user__user_name="Joe")
    	self.assertTrue(query.count() > 0, "Agent wasn't created")
    	joe = query[0]
    	query = AgentCell.objects.filter(user__user_name="Chris")
    	self.assertTrue(query.count() > 0, "Agent wasn't created")
    	print "Joe's user: ", joe.user
    	chris = query[0]
    	query = AgentCell.objects.filter(user__user_name="Alice")
    	self.assertTrue(query.count() > 0, "Agent wasn't created")
    	alice = query[0]
    	# add stories
    	chris.add_read_story("Story 1", [joe.user])
    	joe.add_read_story("Story 2", [chris.user])
    	joe.add_read_story("Story 3", [chris.user])
    	joe.add_read_story("Story 4", [chris.user])
    	joe.add_read_story("Story 5", [alice.user])
    	# invoke cells processing
    	d = datetime.datetime.now().microsecond
    	self.society_cell.process(d)
    	# verify that 2 summary stories were created
    	query = StoryCell.objects.filter(is_aggregation=True)
    	for s in query:
    		print s.name, " -----> ", s.core
    	self.assertEquals(2, query.count(), "Expected that 2 summary stories will be created")
    	

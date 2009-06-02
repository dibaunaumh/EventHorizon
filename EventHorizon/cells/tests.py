"""
Test cases for the cells app.
"""

from django.test import TestCase
from cells.models import *
from event_log.models import *
import datetime


class CellsTest(TestCase):
    def setUp(self):
        query = SocietyCell.objects.all()
        if query.count() > 0:
            self.society_cell = query[0]
        else:
            self.society_cell = SocietyCell()
            self.society_cell.name = "Test domain"
            self.society_cell.layer = 0
            self.society_cell.x = self.society_cell.y = 0
            self.society_cell.core = "A test society"
            self.society_cell.save()
    
    
    def test_add_agent(self):
        """
        Tests that an agent cell was properly created.
        """
        d = datetime.datetime.now().microsecond
        user_name = "joe.%d" % d
        password = "1234"
        new_agent = self.society_cell.add_agent(user_name, password, DATASOURCE_TYPE_TWITTER)
        # test that a user cell was created, with details matching the given user details
        query = UserCell.objects.filter(user_name=user_name)
        self.assertEquals(1, query.count(), "Less or more than 1 matching user found.")
        user = query[0]
        self.assertEquals(password, user.user_password, "User password doesn't match")
        # test that the user cell is a child of the agent cell
        self.assertTrue(user.container != None, "User has no container")
        agent = user.container
        self.assertEquals(new_agent.id, agent.id)
        # test that the agent cell is a child of our society cell
        self.assertEquals(agent.container.id, self.society_cell.id)


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
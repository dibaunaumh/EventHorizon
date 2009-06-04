"""
Test cases for the Twitter Sensor app.
"""
from django.core.handlers.wsgi import WSGIRequest
from django.test.client import Client
from django.test import TestCase
from services import *
from models import *
import twitter

class RequestFactory(Client):
    def request(self, **request):
        environ = {
            'HTTP_COOKIE': self.cookies,
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': 8000,
            'SERVER_PROTOCOL': 'HTTP/1.1',
        }
        environ.update(self.defaults)
        environ.update(request)
        return WSGIRequest(environ)
    
class TwitterSensorTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_tweets_urls(self):
        """
        Tests get_tweets error messages
        """
        rf = RequestFactory()
        request = rf.get('/twitter_sensor/?user=alexars&password=z5fgmeca')
        self.assertEquals(get_tweets(request).content, HttpResponse('Authentication failed. Check your username and password').content)
        request = rf.get('/twitter_sensor/?user=alexarsh')
        self.assertEquals(get_tweets(request).content, HttpResponse('Please enter password for alexarsh').content)
        request = rf.get('/twitter_sensor/')
        self.assertEquals(get_tweets(request).content, HttpResponse('Please enter twitter username').content)
        response = self.client.get('/twitter_sensor/', {'user': 'alexarsh', 'password': 'z5fgmeca'})
        self.assertEquals(response.status_code, 200)

    def test_get_tweets(self):
        """
        Tests get_tweets response
        """
        response = self.client.get('/twitter_sensor/', {'user': 'alexarsh', 'password': 'z5fgmeca'})
        tweets={}
        client = twitter.Api(username='alexarsh', password='z5fgmeca')
        latest_posts = client.GetFriendsTimeline('alexarsh')
        #self.assertEquals(latest_post.count(),)
        for post in latest_posts:
            reply_to_user = ''
            if post.text.startswith("@"):
                reply_to_user = post.text[1:].split(" ")[0]

            user = User()
            user.external_id = post.user.id
            user.name = post.user.name
            user.screen_name = post.user.screen_name
            user.url = post.user.url
            user.location = ''
            user.description = post.user.description
            user.image = post.user.profile_image_url
            user.location = post.user.location

            story = Story()
            story.text = post.text
            story.user_external_id = post.user.id
            story.external_id = post.id
            story.external_url = 'http://twitter.com/%s/status/%s' % (post.user.screen_name, post.id)
            story.in_reply_to_user = reply_to_user
            story.last_update = post.created_at

            tweets[story.text] = user.name;
        self.assertEquals((len(response.content.split('"')) - 1) / 4, len(tweets))
        #checking that we get all the users
        print tweets
        print "--------"
        print response.content
        for u in tweets.values():
            self.assertNotEquals(-1, response.content.find(u))


from django.http import HttpResponse
import simplejson as json
from models import *
import twitter

#def get_tweets(request, since_id, user, password):
def get_tweets(request):
    users = []
    stories = []
    tweets = {}
    if request.GET:
        if 'user' in request.GET and 'password' not in request.GET:
            return HttpResponse('Please enter password for %s' % request.GET['user'])
        if 'user' not in request.GET:
            return HttpResponse('Please enter twitter username')
    else:
        return HttpResponse('Please enter twitter username')
    try:
        client = twitter.Api(username=request.GET['user'], password=request.GET['password'])
        latest_posts = client.GetFriendsTimeline(request.GET['user'])
    except:
        return HttpResponse('Authentication failed. Check your username and password')
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

    #tweets = [users, stories]

    return HttpResponse(json.dumps(tweets))



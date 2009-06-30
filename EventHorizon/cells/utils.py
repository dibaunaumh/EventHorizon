from time import gmtime
import datetime
import twitter
import sys
from event_log.models import log_event
import math


ENGINE_TWITTER_USER_NAME = "EventHorizonEng"
ENGINE_TWITTER_USER_PASSWORD = "fakepassword"



def today():
    t = gmtime()[:3]
    tod = datetime.datetime(t[0], t[1], t[2])
    return tod


def shorten_url(url):
    """Invokes a URL-shortener service for the given URL"""
    # todo implement
    return url


def send_twitter_direct_message(sender, user_name, message, correlation_id=-1):
    """Sends a Twitter direct message to a given user, using the engine's account as sender.
        Uses the TwitterSensor tool as back-end."""
    # todo should be part of the TwitterSensor
    try:
        api = twitter.Api(username=ENGINE_TWITTER_USER_NAME, password=ENGINE_TWITTER_USER_PASSWORD)
        status = api.PostUpdate("d %s %s" % (user_name, message))
        return True
    except:
        context = "%s was trying to tell %s that %s" % (sender, user_name, message)
        if correlation_id != -1:
            context = "%s (processing cycle #%d)" % (context, correlation_id)
        error_message = "Failed to send Twitter direct message: perhaps your connection is broken, or the whale is failing."
        # todo extract the error
        # error_message = " | ".join(sys.exc_info())
        error_message = "%s. %s" % (context, error_message)
        log_event("notification_failed", "AgentCell", sender.id, error_message, correlation_id)
        return False
    
    
def calc_distance(loc0, loc1):
    """Calculate the distance between 2 2D coordinates."""
    if loc1[1] == loc0[1]:
        return abs(loc1[0] - loc0[0])
    if loc1[0] == loc0[0]:
        return abs(loc1[1] - loc0[1])
    return int(math.sqrt(abs(loc1[0]-loc0[0])**2 + abs(loc1[1]-loc0[1])**2))

from django.db import models
from django.utils.translation import gettext_lazy as _
from event_log.models import *
from utils import today, yesterday, shorten_url, send_twitter_direct_message, calc_distance, near_by_location, get_domain
import random
from sqlite3 import IntegrityError
import datetime
import simplejson as json
from django.test.client import Client
import sys

DATASOURCE_TYPE_TWITTER = "Twitter"
DATASOURCE_TYPE_REALITY_TREE = "RealityTree"
DATASOURCE_TYPE_RSS = "RSS"

PROCESSING_CYCLE_STATUS_NOT_STARTED = 0
PROCESSING_CYCLE_STATUS_STARTED = 1
PROCESSING_CYCLE_STATUS_COMPLETED = 2
PROCESSING_CYCLE_STATUS_FAILED = 3

PROCESSING_CYCLE_STATUS_CHOICES = ((PROCESSING_CYCLE_STATUS_NOT_STARTED, "Not started"), 
                                   (PROCESSING_CYCLE_STATUS_STARTED, "Started"), 
                                   (PROCESSING_CYCLE_STATUS_COMPLETED, "Completed"), 
                                   (PROCESSING_CYCLE_STATUS_FAILED, "Failed"))

LAYER_SIZE = 1000

FETCH_STORIES_INTERVAL = 1  # minutes

class LocationCaughtError(ValueError):
    pass


class ProcessingCycle(models.Model):
    status = models.IntegerField(_('status'), default=PROCESSING_CYCLE_STATUS_NOT_STARTED, choices=PROCESSING_CYCLE_STATUS_CHOICES)
    last_update = models.DateTimeField(_('last update'), auto_now=True)
    
    def __unicode__(self):
        return u"%s %d" % (_('Processing cycle'), self.id)



class BaseCell(models.Model):
    """Base cell class, containing most of the common properties ofpp
    a cell: an active entity in a multi-layer composite domain model.
    A cell acts in a 2d grid layer, in which it moves & interacts with
    neighbor cells. Cell normally has a container cell in a higher layer
    & a set of contained cells in a lower layer."""
    name = models.CharField(_('name'), max_length=1000, db_index=True, help_text='The name generated for this cell')
    core = models.TextField(_('core'), help_text=_('The content of a cell'))
    layer = models.IntegerField(_('layer'), help_text=_('The layer in which the cell acts'))
    x = models.IntegerField(_('x'), db_index=True, help_text=_('The x coordinate of the cell within its layer'))
    y = models.IntegerField(_('y'), db_index=True, help_text=_('The y coordinate of the cell within its layer'))
    location = models.CharField(_('location'), db_index=True, unique=True, max_length=30, help_text=_("A representation of the cell's location (e.g., (layer-0, 765, 678) ), used mainly to prevent collisions between cells, using the database uniqueness constraint."))
    container = models.ForeignKey('self', verbose_name=_('container'), related_name="children", null=True, blank=True, help_text=_('The cell containing the cell'))
    child_count = models.IntegerField(_('child count'), default=0, editable=False, help_text=_('how many child cells does the cell have'))
    external_id = models.CharField(_('external id'), max_length=500, null=True, blank=True, help_text=_('The id of the object represented by the cell, in the 3rd party system from which it was obtained.'))
    last_processing_cycle = models.IntegerField(_('last processing cycle'), null=True, blank=True, editable=False, help_text=_('the last processing cycle in which the cell participated'))
    last_processing_time = models.DateTimeField(_('last processing time'), null=True, blank=True, auto_now=True)
    last_update = models.DateTimeField(_('last update'), auto_now=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    
    class Meta:
        abstract = True
        
    
    #def __init__(self, name="Untitled", container=None, core=None, external_id=None):
    #    self.name = name
    #    self.container = container
    #    if self.container:
    #        self.layer = container.layer + 1
    #    else:
    #        self.layer = 0
    #    self.core = core
    #    self.external_id = external_id
    #    self.move_to_random_location()
    
    
    def get_location(self):
        return (self.x, self.y)

    
    def move_to_random_location(self):
        """Tries to create the cell in a random location inside its layer. If the location isn't empty, retries in another location."""
        trials = LAYER_SIZE**2*10
        while trials > 0:
            try:
                return self.move_to(self.get_random_location())
            except:
                # assuming failing due to uniqueness constraint violation. 
                trials = trials - 1

    
    def move_to(self, location):
        """Receives a 2d coordinates of a location as tuple of 2 integers, & tries to set the cell's location to these coordinates. Returns an exception if the location is caught"""
        self.x, self.y = location
        self.location = "(layer-%d, %d, %d)" % (self.layer, self.x, self.y)
        try:
            self.save()
            print "saved:", self, self.x, ",", self.y
            return self.location
        except IntegrityError:  # todo add support for other databases specific exceptions
            print "Failed to move: new location probably already caught"
            raise LocationCaughtError("Location %s is already caught" % self.location)
    
    
    def get_random_location(self):
        """Returns random 2d coordinates in the dimensions of the layer."""
        return (random.randint(0, LAYER_SIZE-1), random.randint(0, LAYER_SIZE-1))
    
    
    def get_cell_at_location(self, x, y):
        """Returns the celll at the given location, or None in case the location is empty."""
        query = BaseCell.objects.filter(x = x, y = y)
        if query.count() > 0:
                return query[0]
        return None
    
    
    def reduce_to_subclass(self):
        """Hack: tries to load the instance from a subclass of BaseCell, according to its layer"""
        if self.layer == 0:
            return SocietyCell.objects.get(pk=self.id)
        elif self.layer == 1:
            return AgentCell.objects.get(pk=self.id)
        elif self.layer == 2:
            try:
                return UserCell.objects.get(pk=self.id)
            except:
                return StoryCell.objects.get(pk=self.id)
            

    def process(self, process_cycle_id=-1):
        """Recursively invokes the processing of the child cells."""
        # todo create a processing cycle, & use its id as correlation id
        log_event("process", "BaseCell", self.id, "Invoking child cells process method", process_cycle_id)
        for child in self.children.all():
            # hack alert: need to figure out how to do this properly
            real_child = child.reduce_to_subclass()
            real_child.process(process_cycle_id) 
            child.process(process_cycle_id)
    

    class Meta:
        verbose_name = _("base cell")
        verbose_name_plural = _("base cells")
    
        
    def __unicode__(self):
        return u"[%s] %s" % (_("Agent"), self.name)





class SocietyCell(BaseCell):
    """Represents a complete engine modeling a domain & trying to
    draw conclusions out of it. Normally has cardinality of 1 in an
    instance of the engine. Directly contains & manages Agent cells handling
    parts of the domain."""
    domain_name = models.CharField(_('domain name'), null=True, blank=True, max_length=400, help_text=_("the name of the domain modeled by the society"))
    domain_description = models.CharField(_('domain description'), null=True, blank=True, max_length=4000, help_text=_("a description of the domain modeled by the society"))
    domain_url = models.URLField(_('domain url'), null=True, blank=True, help_text=_("a URL of the domain modeled by the society"))
    
    
    #def __init__(self, name="Untitled", domain_name=None, domain_description=None, domain_url=None):
    #    BaseCell.__init__(self, name)
    #    self.domain_name = domain_name
    #    self.domain_description = domain_description
    #    self.domain_url = domain_url
    
    
    #class Meta(BaseCell.Meta):
    #    verbose_name = _("society cell")
    #    verbose_name_plural = _("society cells")
        

    def add_agent(self, user_name, user_password, datasource_type):
        """Creates a child agent cell"""
        # 1st create a user
        user = UserCell()
        user.name = user_name
        user.user_name = user_name
        user.user_password = user_password
        user.layer = self.layer + 2
        user.move_to_random_location()
        # now create an agent for that user
        name = u"%s %s" % (_("Agent for"), user_name)
        agent = AgentCell()
        agent.container = self
        agent.user = user
        agent.name = name
        agent.datasource_type = datasource_type
        agent.layer = self.layer + 1
        agent.move_to_random_location()
        user.container = agent
        return agent


    def process(self, correlation_id=-1):
        log_event("process", "SocietyCell", self.id, "Not doing nothing", correlation_id)
        # todo implement
        BaseCell.process(self, correlation_id)
        self.last_processing_cycle = correlation_id
        self.save()



    def __unicode__(self):
        return u"[%s] %s" % (_("Society"), self.name)



class UserCell(BaseCell):
    """Represents a user"""
    user_name = models.CharField(_('user name'), unique=True, max_length=400, help_text=_('user name used for authentication against the datasource'))
    user_password = models.CharField(_('user password'), max_length=500, help_text=_('user password used for authentication against the datasource'))
    user_full_name = models.CharField(_('user full name'), null=True, blank=True, max_length=600, help_text=_('user full name'))
    user_email = models.CharField(_('user email'), null=True, blank=True, max_length=600, help_text=_('user email'))
    user_im = models.CharField(_('user IM'), null=True, blank=True, max_length=600, help_text=_('user instant messaging screen name'))
    user_location = models.CharField(_('user location'), null=True, blank=True, max_length=400, help_text=_('user location'))
    user_bio = models.CharField(_('user bio'), null=True, blank=True, max_length=1000, help_text=_('user short biography'))
    user_age = models.IntegerField(_('user age'), null=True, blank=True, help_text=_('user age'))
    user_gender = models.CharField(_('user gender'), null=True, blank=True, max_length=1, choices=(("M", "Male"), ("F", "Female")), help_text=_('user gender'))
    
    
    #def __init__(self, name, container, user_name, datasource_type, core=None, external_id=None):
    #    super.__init__(name, container, core, external_id)
    #    self.user_name = user_name
    #    self.user_password = user_password
    #    self.user_full_name = user_full_name
    #    self.user_location = user_location
    #    self.user_bio = user_bio
    #    self.user_age = user_age
    #    self.user_gender = user_gender
    #    add_concept()


    def add_concept(self):
        pass


    def process(self, correlation_id=-1):
        log_event("process", "UserCell", self.id, "Not doing nothing", correlation_id)
        # todo implement
        self.last_processing_cycle = correlation_id
        self.save()




class StoryCell(BaseCell):
    """Directly contains Concept & Statement cells."""
    authors = models.ManyToManyField(UserCell, verbose_name=_('authors'), related_name='outgoing_stories', null=True, blank=True, help_text=_('who are the authors of the story'))
    recipients = models.ManyToManyField(UserCell, verbose_name=_('recipients'), related_name='incoming_stories', null=True, blank=True, help_text=_('users to whom the story will be delivered'))
    is_aggregation = models.BooleanField(_('is aggregation'), default=False, help_text=_('whether the story is an aggregation/summary of one or more other stories'))
    aggregated_stories = models.ManyToManyField('self', verbose_name=_('aggregated stories'), null=True, blank=True, help_text=_('stories aggregated/summarized by this story'))


    def __unicode__(self):
        return u"[%s] %s" % (_('Story'), self.name)


    def get_absolute_url(self):
        return "http://%s/cells/view/story/%d" % (get_domain(), self.id)


    def process(self, correlation_id=-1):
    	"""Story cells have 3 main behaviors: 
        - translating their content to semantic cells; 
        - changing location to reflect semantic orientation; 
        - generating summary stories."""
        # if needed, update summary stories
        print "Story %d created at" % self.id, self.created_at
        tod = today()
        if self.created_at >= tod:
            log_event("process", "StoryCell", self.id, "Updating summary stories", correlation_id)
            self.update_summary_stories()
        # move to a location, maximizing the value of the story
        self.move()
        self.last_processing_cycle = correlation_id
        self.save()


    def find_possible_movement_targets(self):
        """A cell can move in steps of up to 5 squares, so list the possible location in that distance."""
        targets = []
        for x in range(self.x - 5, self.x + 5):
            for y in range(self.y - 5, self.y + 5):
                if (x, y) != (self.x, self.y):
                    if 0 < x < LAYER_SIZE and 0 < y < LAYER_SIZE:
                        targets.append( (x, y) )
        return targets


    def evaluate_possible_movement_targets(self, possible_targets):
        """The value of a story location is highest when its distance from its author is 40, 
           so determine the value of all possible target locations accordingly."""
        result = []
        # find the goal location - near either the author of the story, or its recipient (in case there's no author)
        if self.authors.all().count() > 0:
            author = self.authors.all()[0]
            goal_location = (author.x, author.y)
        elif self.recipients.all().count() > 0:
            recipient = self.recipients.all()[0]
            goal_location = (recipient.x, recipient.y)
        else:
            goal_location = None
        # move toward the goal location
        if goal_location != None:
            goal_location = near_by_location(goal_location, min_distance=20, max_distance=40, limit=LAYER_SIZE)
            for loc in possible_targets:
                value = -calc_distance(goal_location, loc)
                result.append( (value, loc)  )
        else :
            result = [ (0, i) for i in possible_targets]
        return result


    def move(self):
        # todo implement
        possible_movement_targets = self.find_possible_movement_targets()
        if len(possible_movement_targets) > 0:
            evaluated_movement_targets = self.evaluate_possible_movement_targets(possible_movement_targets)
            evaluated_movement_targets.sort()
            done = False
            # todo limit to max trials
            while not done:
                try:
                    max_value_target = evaluated_movement_targets[-1]
                    self.move_to(max_value_target[1])
                    done = True
                except LocationCaughtError:
                    del evaluated_movement_targets[-1]


    def update_summary_stories(self):
        """Unless this story is a summary story, loop on all recipients, look-up or create a summary story, & add itself to it."""
        if self.is_aggregation:
            return
        # update the summary story for all recipients
        for user in self.recipients.all():
            # look up a summary story for that user: 
            # - it should be marked as is_aggregation
            # - it should have the user as recipient
            # - it should be from today
            tod = today()
            query = StoryCell.objects.filter(is_aggregation=True, recipients__pk=user.id, last_update__gte=tod)
            if query.count() > 0:
                summary_story = query[0]
            else:
                # if not found, create one
                summary_story = StoryCell()
                summary_story.name = "%s's %s %s" % (user.name, _('summary for'), tod.strftime("%c"))
                summary_story.container = self.container
                summary_story.layer = self.layer
                summary_story.is_aggregation = True
                summary_story.move_to_random_location()
                summary_story.recipients.add(user)
            # add the story to the summary
            summary_story.aggregated_stories.add(self)
            summary_story.generate_summary()


    def generate_summary(self):
    	"""Generate a summary story based on the aggregated stories"""
        recipient = self.recipients.all()[0]
        tod = datetime.datetime.today()
        authors_map = {}
        for story in self.aggregated_stories.filter(last_update__gte=today()):
            for author in story.authors.all():
                if authors_map.has_key(author):
                    authors_map[author] = authors_map[author] + 1
                else:
                   authors_map[author] = 1
        # todo use template
        summary = "<h3>Summary for %s</h3>" % recipient
        for author, count in authors_map.items():
            summary = summary + "<li><a href='http://twitter.com/%s' target='_blank'>%s</a> twitted since yesterday %d <a href='http://search.twitter.com?q=from:%s' target='_blank'>tweets</a>" % (author.user_name, author, count, author.user_name)
        self.core = summary
        self.save()


class AgentCell(BaseCell):
    """Represents a part of the domain, and responsible for interacting
    with the systems representing it, e.g., end users. For that sake, an 
    agent cell receives the details of a user representing the domain,
    to be used for fetching the stories depicting the domain from the datasource.
    Directly contains & manages Story & User cells containing these stories."""
    user = models.ForeignKey(UserCell)
    datasource_type = models.CharField(_('datasource type'), max_length=100, help_text=_('the type of datasource, from which to fetch stories, e.g., TWITTER_FRIENDS_TIMELINE'))
    last_story = models.CharField(_('last story'), max_length=100, null=True, blank=True, help_text=_('external id of the last story fetched.'))
    last_summary_delivered_at = models.DateTimeField(_('last summary delivered at'), null=True, blank=True)
    last_story_fetched_at = models.DateTimeField(_('last story fetched at'), null=True, blank=True)


    #def __init__(self, name, container, datasource_type, user_name, user_password, user_full_name=None, user_email=None, 
    #             user_im=None, user_location=None, user_bio=None, user_age=None, user_gender=None, core=None, external_id=None):
    #    super.__init__(name, container, core, external_id)
    #    self.datasource_type = datasource_type
    #    self.add_user(user_name, user_password, user_full_name, user_email, user_im, user_location, user_bio, user_age, user_gender)
        
        
    def add_user(self, user_name):
        """Creates a child User cell"""
        user = UserCell()
        user.name = user_name
        user.user_name = user_name
        user.user_password = "123456"
        user.save()
    
    def add_read_story(self, text, authors):
        """Creates a StoryCell with the given text & authors. Sets the agent's user as the story recipient."""
        story = StoryCell()
        story.name = text
        story.container = self
        story.core = text
        story.layer = self.layer + 1
        story.move_to_random_location()
        story.recipients.add(self.user)
        for author in authors:
            story.authors.add(author)
        story.save()


    def fetch_stories(self, correlation_id=-1):
        """Fetches new stories from the datasource. Uses the last story external id to 
        fetch only new stories."""
        try:
            #url = "http://%s/twitter_sensor/?user=%s&password=%s" % (get_domain(), self.user.user_name, self.user.user_password)
            #url = "http://%s/twitter_sensor/?user=%s&password=%s" % (self.get_domain(), self.user.user_name, self.user.user_password)
            client = Client()
            tweets = client.get('http://%s/twitter_sensor/' % get_domain(), {'user': self.user.user_name, 'password': self.user.user_password}).content
            tweets = json.loads(tweets)
            for key in tweets:
                try :
                    authors = []
                    authors.append(tweets[key])
                    self.add_read_story(key, authors)
                    self.add_user(tweets[key])
                except:
                    log_event("fetch_stories_failed", "AgentCell", self.id, "Adding fetched story %s failed, for %s" % (key, self.user), correlation_id)
        except:
            print sys.exc_info()
            log_event("fetch_stories_failed", "AgentCell", self.id, "Failed to fetch stories for %s" % self.user, correlation_id)


    def process(self, correlation_id=-1):
        log_event("process", "AgentCell", self.id, "Fetching stories", correlation_id)
        # if needed send summary story
        t = datetime.datetime.now()
        if self.last_summary_delivered_at == None or (t - self.last_summary_delivered_at).days > 1:
            self.send_daily_summary(correlation_id)
        few_minutes_ago = t + datetime.timedelta(seconds=-(FETCH_STORIES_INTERVAL*60))
        if self.last_story_fetched_at == None or self.last_story_fetched_at < few_minutes_ago:
            self.fetch_stories(correlation_id)
        self.last_processing_cycle = correlation_id
        self.save()


    def send_daily_summary(self, correlation_id=-1):
        """Sends the generated summary story for its recipient"""
        # look up a summary
        tod = today()
        query = StoryCell.objects.filter(is_aggregation=True, recipients__pk=self.user.id, last_update__gte=tod)
        if query.count() > 0:
            summary_story = query[0]
            # if found, send a link to it the user
            log_event("notify", "Agent", self.id, "Sending summary story to user %s" % self.user.user_name, correlation_id)
            link = summary_story.get_absolute_url()
            shortened_url = shorten_url(link)
            message = "Here's your daily summary for %s: %s" % (tod, shortened_url)
            if send_twitter_direct_message(self, self.user.user_name, message, correlation_id):
                self.last_summary_delivered_at = datetime.datetime.now()
                self.save()


    #class Meta(BaseCell.Meta):
    #    verbose_name = _("agent cell")
    #    verbose_name_plural = _("agent cells")
        

    def __unicode__(self):
        return u"[%s] %s" % (_("Agent"), self.name)
    
    
    
class ConceptCell(BaseCell):
    """Represents a semantic concept"""
    pass



class StatementCell(BaseCell):
    """Represents a semantic statement describing concepts & instances"""
    pass


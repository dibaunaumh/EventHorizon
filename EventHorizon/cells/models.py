from django.db import models
from django.utils.translation import gettext_lazy as _
from event_log.models import *
import random
from sqlite3 import IntegrityError


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
    

    def process(self, process_cycle_id=-1):
        """Recursively invokes the processing of the child cells."""
        # todo create a processing cycle, & use its id as correlation id
        log_event("process", "BaseCell", -1, "Invoking child cells process method", process_cycle_id)
        for child in self.children.all():
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
        print "fucking got here"
        user.container = agent
        return agent


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





class AgentCell(BaseCell):
    """Represents a part of the domain, and responsible for interacting
    with the systems representing it, e.g., end users. For that sake, an 
    agent cell receives the details of a user representing the domain,
    to be used for fetching the stories depicting the domain from the datasource.
    Directly contains & manages Story & User cells containing these stories."""
    user = models.ForeignKey(UserCell)
    datasource_type = models.CharField(_('datasource type'), max_length=100, help_text=_('the type of datasource, from which to fetch stories, e.g., TWITTER_FRIENDS_TIMELINE'))
    last_story = models.CharField(_('last story'), max_length=100, null=True, blank=True, help_text=_('external id of the last story fetched.'))


    #def __init__(self, name, container, datasource_type, user_name, user_password, user_full_name=None, user_email=None, 
    #             user_im=None, user_location=None, user_bio=None, user_age=None, user_gender=None, core=None, external_id=None):
    #    super.__init__(name, container, core, external_id)
    #    self.datasource_type = datasource_type
    #    self.add_user(user_name, user_password, user_full_name, user_email, user_im, user_location, user_bio, user_age, user_gender)
        
        
    def add_user(self):
        """Creates a child User cell"""
        user = UserCell()
    
    
    def fetch_stories(self):
        """Fetches new stories from the datasource. Uses the last story external id to 
        fetch only new stories."""
        pass


    #class Meta(BaseCell.Meta):
    #    verbose_name = _("agent cell")
    #    verbose_name_plural = _("agent cells")
        

    def __unicode__(self):
        return u"[%s] %s" % (_("Agent"), self.name)
    
    
    
class StoryCell(BaseCell):
    """Directly contains Concept & Statement cells."""
    pass




class ConceptCell(BaseCell):
    """Represents a semantic concept"""
    pass



class StatementCell(BaseCell):
    """Represents a semantic statement describing concepts & instances"""
    pass


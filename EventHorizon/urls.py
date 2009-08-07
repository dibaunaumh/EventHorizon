from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import os 

base_dir = os.path.abspath(os.path.dirname(__file__))

urlpatterns = patterns('',
    # Example:
    (r'^cells/', include('cells.urls')),
    (r'^twitter_sensor', include ('twitter_sensor.urls')),
    (r'^text_analyzer', include ('text_analyzer.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '%s/media' % base_dir}),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    
    (r'^$', 'cells.views.home'),
    
)

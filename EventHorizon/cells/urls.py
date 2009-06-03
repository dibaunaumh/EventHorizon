from django.conf.urls.defaults import *


urlpatterns = patterns('',
    (r'^layer/(?P<layer>\d+)$', 'cells.services.get_layer_cells'),
)

from django.conf.urls.defaults import *


urlpatterns = patterns('',
    (r'^$', 'cells.services.get_all_layers_cells'),
    (r'^layer/(?P<layer>\d+)$', 'cells.services.get_layer_cells'),
    (r'^process/(?P<cell_id>\d+)', 'cells.services.process'),
    (r'^view/story/(?P<cell_id>\d+)', 'cells.views.view_story_cell'),
)

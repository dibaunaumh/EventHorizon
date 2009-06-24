from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from cells.models import *



def home(request):
    """Renders the engine view page"""
    nagents = AgentCell.objects.all().count()
    return render_to_response('cells/engine.html', locals())


def view_story_cell(request, cell_id):
    """Renders a Story Cell"""
    cell = get_object_or_404(StoryCell, pk=cell_id)
    return render_to_response('cells/story.html', locals())
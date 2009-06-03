from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from cells.models import *



def home(request):
    nagents = AgentCell.objects.all().count()
    return render_to_response('cells/engine.html', locals())
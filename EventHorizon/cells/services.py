from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core import serializers
from cells.models import *


def get_layer_cells(request, layer):
    query = BaseCell.objects.filter(layer=layer)
    data = serializers.serialize("json", query)
    return HttpResponse(data)

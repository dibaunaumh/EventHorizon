from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core import serializers
from cells.models import *
from event_log import *
import sys


CORRELATION_ID = "correlation_id" 


def get_all_layers_cells(request):
    """Returns all cells within a given layer, in JSON format"""
    if "q" in request.GET:
        filter_keywords = request.GET["q"]
    else:
        filter_keywords = None
    print "get cells with filter %s" % filter_keywords
    data = []
    for layer in range(4):
        if filter_keywords:
            query = BaseCell.objects.filter(layer=layer, core__contains=filter_keywords)
        else:
            query = BaseCell.objects.filter(layer=layer)
        if query.count() > 0:
            #layer_cells = [cell.reduce_to_subclass() for cell in query]    # doesn't include basecell attributes
            data.append(serializers.serialize("json", query))
        else:
            data.append("[]")
    data = "[%s]" % ",".join(data)
    return render_to_response("cells/cells.json", locals())


def get_layer_cells(request, layer):
    """Returns all cells within a given layer, in JSON format"""
    query = BaseCell.objects.filter(layer=layer)
    data = serializers.serialize("json", query)
    return HttpResponse(data)


def process(request, cell_id):
    """Invokes the process method of the cell with the given id, or HTTP 404 if not found."""
    cell = get_object_or_404(BaseCell, pk=cell_id)
    cycle = ProcessingCycle()
    cycle.save()
    log_event("processing_invoked", "BaseCell", cell_id, "Processing invoked", correlation_id=cycle.id)
    try:
        cell.process(cycle.id)
        cycle.status = PROCESSING_CYCLE_STATUS_COMPLETED
        cycle.save()
        log_event("processing_completed", "BaseCell", cell_id, "Processing completed", correlation_id=cycle.id)
    except:
        print sys.exc_info()
        cycle.status = PROCESSING_CYCLE_STATUS_FAILED
        cycle.save()
        log_event("processing_failed", "BaseCell", cell_id, "Processing failed", correlation_id=cycle.id)
    log = get_log(cycle.id)
    return render_to_response("cells/processing_log.html", locals())

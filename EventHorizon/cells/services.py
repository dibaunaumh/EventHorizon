from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core import serializers
from cells.models import *
from event_log import *


CORRELATION_ID = "correlation_id" 


def get_layer_cells(request, layer):
    """Returns all cells within a given layer"""
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
        cycle.status = PROCESSING_CYCLE_STATUS_FAILED
        cycle.save()
        log_event("processing_failed", "BaseCell", cell_id, "Processing failed", correlation_id=cycle.id)
    log = get_log(cycle.id)
    return render_to_response("cells/processing_log.html", locals())
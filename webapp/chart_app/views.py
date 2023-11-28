import os

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.shortcuts import render

from core.models import ShiftModel


def chart_view(request, **kwargs):
    shifts = ShiftModel.objects.all()

    # Prepare data for rendering the chart
    chart_data = {
        'shift_labels': [f'Shift {shift.id}' for shift in shifts],
        'cumulative_good_time': [shift.good_time.total_seconds() if shift.good_time else 0 for shift in shifts],
        'cumulative_bad_time': [shift.bad_time.total_seconds() if shift.bad_time else 0 for shift in shifts],
        'cumulative_lost_time': [shift.lost_time.total_seconds() if shift.lost_time else 0 for shift in shifts],
    }

    # Prepare data for JSON response
    json_data = {
        'data': {
            'Shift': chart_data['shift_labels'],
            'Cumulative Good Time': chart_data['cumulative_good_time'],
            'Cumulative Bad Time': chart_data['cumulative_bad_time'],
            'Cumulative Lost Time': chart_data['cumulative_lost_time'],
        }
    }
    # Check if the request is an AJAX request

    if request.is_ajax():
        return JsonResponse(json_data)

    # Render the HTML page with the chart
    context = {'chart_data': chart_data}
    return render(request, 'charts/chart1.html', context)
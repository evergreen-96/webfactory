from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from core.buisness import *
from core.models import CustomUserModel


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def chart_view(request, **kwargs):
    shifts = ShiftModel.objects.all()

    # Prepare data for rendering the chart
    chart_data = {
        'shift_labels': [f'Shift {shift.id}' for shift in shifts],
        'cumulative_good_time': [shift.good_time.total_seconds() if shift.good_time else 0 for shift in shifts],
        'cumulative_bad_time': [shift.bad_time.total_seconds() if shift.bad_time else 0 for shift in shifts],
        'cumulative_lost_time': [shift.lost_time.total_seconds() if shift.lost_time else 0 for shift in shifts],
    }

    # Aggregate the counts of solved and unsolved reports
    reports_data = (ReportsModel.objects.filter(user=request.user.customusermodel)
                    .values('is_solved').annotate(count=Count('id')))

    # Extract counts from the aggregated data
    solved_reports = next((item['count'] for item in reports_data if item['is_solved']), 0)
    unsolved_reports = next((item['count'] for item in reports_data if not item['is_solved']), 0)

    # Prepare data for JSON response
    json_data = {
        'data': {
            'Shift': chart_data.get('shift_labels', []),
            'Cumulative Good Time': chart_data.get('cumulative_good_time', []),
            'Cumulative Bad Time': chart_data.get('cumulative_bad_time', []),
            'Cumulative Lost Time': chart_data.get('cumulative_lost_time', []),
            'Solved Reports': solved_reports,
            'Unsolved Reports': unsolved_reports,
        }
    }

    if is_ajax(request):
        return JsonResponse(json_data, safe=False)

    # Render the HTML page with the chart
    context = {'chart_data': chart_data}
    return render(request, 'charts/chart1.html', context)
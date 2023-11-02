from datetime import timedelta
from types import NoneType

from PIL import Image
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from pyzbar.pyzbar import decode

from core.decorators import check_prev_page
from core.models import CustomUserModel, StatDataModel, StatBugsModel, \
    StatOrdersModel


def count_bugs_duration(last_order):
    """
    count bugs duration in last order
    return: timedelta
    """
    total_bugs = StatBugsModel.objects.filter(order=last_order).filter(is_solved=True)
    total_duration = timedelta()

    for bug in total_bugs:
        one_bug_duration = bug.bug_end_time - bug.bug_start_time
        total_duration += one_bug_duration
    return total_duration


def decode_photo(request):
    """
    API endpoint to /qr-decoder/
    decode image_data
    request: request
    return :str
    """
    image_data = request.FILES.get('image')
    image = Image.open(image_data)
    resized = image.resize((500, 500))
    decoded_qr_img = decode(resized)
    try:
        cropped_data = decoded_qr_img[0].data
        decoded_qr_data = cropped_data.decode('utf-8')
    except IndexError:
        decoded_qr_data = 'Ошибка в декодировании'
    return HttpResponse(decoded_qr_data)


@login_required
def main_page(request):
    # устанавливает сессию, чтобы нельзя было войти на страницу
    request.session['prev_page'] = True
    user_profile = CustomUserModel.objects.get(user=request.user)
    last_order = StatOrdersModel.objects.filter(user=user_profile).last()
    context = {
        'custom_user': user_profile,
        'current_time': timezone.now(),
    }

    if request.method == 'POST' and last_order is not NoneType:
        shift = StatDataModel(
            user=user_profile,
            shift_start_time=timezone.now(),
            shift_end_time=None,
            num_ended_orders=0,
            shift_time_total=None,
            good_time=None,
            bad_time=None,
            lost_time=None,
            total_bugs_time=None,
        )
        shift.save()

        order = StatOrdersModel(
            user=user_profile,
            stat_data = shift,
            part_name='',
            num_parts=0,
            order_start_time=None,
            order_scan_time=None,
            order_start_working_time=None,
            order_machine_start_time=None,
            order_machine_end_time=None,
            order_end_working_time=None,
            order_bugs_time=None
        )
        order.save()
        return redirect('shift_main_page')
    return render(request, 'include/user_inf_start_shift.html', context)


def shift_main_page(request):
    request.session['parts_done'] = 0
    request.session['prev_page'] = False
    user_profile = CustomUserModel.objects.get(user=request.user)
    last_order = StatOrdersModel.objects.filter(user=user_profile).last()
    last_shift = StatDataModel.objects.filter(user=user_profile).last()
    current_time = timezone.now()
    context = {
        'custom_user': user_profile,
        'current_time': current_time,
    }

    if request.method == 'POST' and 'endShift' not in request.POST:
        last_order.order_start_time = timezone.now()
        last_order.save()
        return redirect('shift_scan')
    elif request.method == 'POST' and 'endShift' in request.POST:
        last_shift.shift_end_time = timezone.now()
        num_orders = StatOrdersModel.objects.filter().count()
        last_shift.save()

        return redirect('main')

    return render(request, 'include/shift_first_page.html', context)


@csrf_exempt
def shift_scan(request):
    user_profile = CustomUserModel.objects.get(user=request.user)
    last_order = StatOrdersModel.objects.filter(user=user_profile).last()
    if request.method == 'POST':
        partname = request.POST.get('partname')
        last_order.part_name = partname
        last_order.order_scan_time = timezone.now()
        last_order.save()
        return redirect('shift_part_qaun')
    return render(request, 'include/shift_scan.html')


def shift_part_qaun(request):
    selected_value = request.POST.get('quantity', '')
    button_value = request.POST.get('button', '')
    selected_button = selected_value if selected_value else button_value
    user_profile = CustomUserModel.objects.get(user=request.user)
    last_order = StatOrdersModel.objects.filter(user=user_profile).last()
    if request.method == 'POST':
        last_order.num_parts = selected_value
        last_order.order_start_working_time = timezone.now()
        last_order.save()
        return redirect('shift_setup')
    return render(request, 'include/shift_part_qaun.html',
                  {'selected_value': selected_button})


def shift_setup(request):
    user_profile = CustomUserModel.objects.get(user=request.user)
    last_order = StatOrdersModel.objects.filter(user=user_profile).last()
    context = {
        'custom_user': user_profile,
    }

    if request.method == 'POST':
        last_order.order_machine_start_time = timezone.now()
        last_order.save()
        return redirect('shift_processing')
    return render(request, 'include/shift_setup.html', context)


def shift_processing(request):
    user_profile = CustomUserModel.objects.get(user=request.user)
    last_order = StatOrdersModel.objects.filter(user=user_profile).last()

    if request.method == 'POST':
        last_order.order_machine_end_time = timezone.now()
        last_order.save()
        return redirect('shift_ending')
    return render(request, 'include/shift_processing.html')


def shift_ending(request):
    user_profile = CustomUserModel.objects.get(user=request.user)
    last_order = StatOrdersModel.objects.filter(user=user_profile).last()

    if request.method == 'POST':
        last_order.order_end_working_time = timezone.now()
        last_order.save()
        last_order.order_bugs_time = count_bugs_duration(last_order)
        last_order.save()
        return redirect('shift_main_page')
    return render(request, 'include/shift_ending.html')


def error_report(request):
    user_profile = CustomUserModel.objects.get(user=request.user)
    last_order = StatOrdersModel.objects.filter(user=user_profile).last()
    user_reports = StatBugsModel.objects.filter(user=user_profile).last()
    context = {
        'custom_user': user_profile,
        'users_reports': user_reports
    }

    if request.method == 'POST':
        new_bug = StatBugsModel(
            user=CustomUserModel.objects.get(user=request.user),
            order=last_order,
            bug_description=request.POST.get('bug_description'),
            bug_end_time=None
        )
        new_bug.save()
    return render(request, 'include/error_report.html', context)

from datetime import timedelta
from functools import reduce
from types import NoneType

from PIL import Image
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Sum, ExpressionWrapper, F, fields
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from pyzbar.pyzbar import decode

from core.decorators import check_prev_page
from core.models import CustomUserModel, StatDataModel, StatBugsModel, \
    StatOrdersModel, PositionsModel


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


def create_or_get_last_order(user_profile, shift):
    # Проверка, если смена не закончилась, то создаем новый заказ, иначе получаем последний
    if shift.shift_end_time is None:
        last_order = StatOrdersModel(
            user=user_profile,
            stat_data=shift,
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
        last_order.save()
    else:
        last_order = StatOrdersModel.objects.filter(user=user_profile).last()

    last_order.order_start_time = timezone.now()
    last_order.save()
    return last_order


def end_shift(shift):
    # Устанавливаем shift_end_time
    shift.shift_end_time = timezone.now()

    # Считаем количество заказов
    shift.num_ended_orders = StatOrdersModel.objects.filter(stat_data=shift).count()

    # Считаем общее время смены
    shift.shift_time_total = shift.shift_end_time - shift.shift_start_time

    # Считаем время багов
    total_bugs_time = StatOrdersModel.objects.filter(stat_data=shift).aggregate(
        total_bugs_time=Sum('order_bugs_time')
    )['total_bugs_time']
    shift.total_bugs_time = total_bugs_time or timedelta()

    # Считаем полезное время (good_time)
    duration_expression = ExpressionWrapper(
        F('order_machine_end_time') - F('order_machine_start_time'),
        output_field=fields.DurationField()
    )
    total_good_time = StatOrdersModel.objects.filter(stat_data=shift).annotate(
        good_time=Sum(duration_expression, output_field=fields.DurationField())
    ).aggregate(total_good_time=Sum('good_time'))['total_good_time']
    shift.good_time = total_good_time or timedelta()

    # Считаем бесполнезное время (bad_time)
    total_bad_time = timedelta()

    for order in StatOrdersModel.objects.filter(stat_data=shift):
        bad_time_in_order = (
                order.order_end_working_time - order.order_scan_time -
                (order.order_machine_end_time - order.order_machine_start_time) +
                order.order_bugs_time
        )
        total_bad_time += bad_time_in_order

    shift.bad_time = total_bad_time
    shift.save()
    # Считаем время рассоса (lost_time)
    chill_time = PositionsModel.objects.get(position_name=shift.user.position).chill_time
    chill_time_parts = chill_time.split(':')
    chill_timedelta = timedelta(
        hours=int(chill_time_parts[0]),
        minutes=int(chill_time_parts[1]),
        seconds=int(chill_time_parts[2])
    )
    total_lost_time = (
            shift.shift_time_total -
            shift.good_time - shift.bad_time -
            shift.total_bugs_time - chill_timedelta
    )

    shift.lost_time = total_lost_time
    shift.save()



@login_required
def main_page(request):
    """
    Заглавная страница сайта
    """
    # устанавливает сессию, чтобы нельзя было войти на страницу
    request.session['prev_page'] = True
    request.session['visit'] = 0
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
        return redirect('shift_main_page')
    return render(request, 'include/user_inf_start_shift.html', context)


def shift_main_page(request):
    """
    Страница начала смены
    (можно начать новую деталь или закончить смену)
    """
    # Устанавливает сессию, чтобы нельзя было войти на страницу
    request.session['prev_page'] = False
    user_profile = CustomUserModel.objects.get(user=request.user)
    shift = StatDataModel.objects.filter(user=user_profile).last()
    current_time = timezone.now()
    context = {
        'custom_user': user_profile,
        'current_time': current_time,
    }

    if request.method == 'POST':
        if 'endShift' not in request.POST:
            last_order = create_or_get_last_order(user_profile, shift)
            return redirect('shift_scan')
        elif 'endShift' in request.POST:
            end_shift(shift)
            return redirect('main')

    return render(request, 'include/shift_first_page.html', context)


@csrf_exempt
def shift_scan(request):
    """
    Страница сканирование QR
    """
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
    """Страница выбора количества деталей"""
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

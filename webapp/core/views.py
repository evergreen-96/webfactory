from collections import defaultdict

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models.expressions import NoneType, Case, When
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_control
from django.views.generic import TemplateView

from core.buisness import *
from core.forms import ReportEditForm
from core.models import CustomUserModel


def login_view(request):
    """
       Handles the login functionality.
       Parameters:
           request (HttpRequest): The HTTP request object.
       Returns:
           HttpResponse: The HTTP response object.
       Description:
           This function handles the login functionality. It checks if the request method is POST,
           retrieves the username and password from the request, authenticates the user,
           and if the authentication is successful,
           logs in the user and redirects them to the 'main' page.
           If the authentication fails, it displays an error message.
           If the request method is not POST, it renders the 'login.html' template.
       """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')

    return render(request, 'include/login.html')


def logout_view(request):
    """
    Logs out the user by invalidating the current session and redirecting to the 'main' page.
    :param request: The HTTP request object.
    :type request: HttpRequest
    :return: A redirect response to the 'main' page.
    :rtype: HttpResponseRedirect
    """
    logout(request)
    return redirect('main')


def pre_shift_view(request):
    """
    Начать смену или выйти из системы
    """
    custom_user = CustomUserModel.objects.filter(user=request.user.id).last()
    context = {
        'user': request.user,
        'custom_user': custom_user,
    }
    if request.method == 'POST':
        if 'start_shift' in request.POST:
            return redirect('shift_main_page')
    return render(request, 'include/shift/pre_shift_page.html', context)


@login_required
def shift_main_view(request):
    """
    Главная страница смены
    """
    custom_user = CustomUserModel.objects.get(id=request.user.id)
    machines = custom_user.machine.all()
    shift = get_last_or_create_shift(custom_user)
    has_unsolved_reports = ReportsModel.objects.filter(
        order__related_to_shift=shift, is_solved=False
    ).exists()
    context = {
        'user': request.user,
        'custom_user': custom_user,
        'machines': machines,
        'has_unsolved_reports': has_unsolved_reports,
    }
    if request.method == 'POST':
        selected_machine_id = request.POST.get('selected_machine_id')
        request.session['selected_machine_id'] = selected_machine_id
        if 'continue' in request.POST:
            order = get_order(custom_user, shift, selected_machine_id)
            url = order.hold_url
            if type(url) is NoneType:
                url = ReportsModel.objects.filter(order__machine_id=selected_machine_id).last().url
            remove_hold(order)
            return redirect(url)
        if 'start_new' in request.POST:
            start_new_order(custom_user, shift, selected_machine_id)
            return redirect('shift_scan_page')
        if 'stop_working' in request.POST:
            order = get_order(custom_user, shift, selected_machine_id)
            stop_order(order)
            return redirect('shift_main_page')
        if 'end_shift' in request.POST:
            if not is_all_orders_ended(shift):
                messages.error(request, 'Завершите работу на всех станках!')
                return redirect('shift_main_page')
            count_and_end_shift(shift)
            return redirect('main')
    return render(request, 'include/shift/main_page.html', context)


def order_scan_view(request):
    custom_user = CustomUserModel.objects.filter(user=request.user.id).last()
    shift = get_last_or_create_shift(custom_user)
    order = get_order(custom_user, shift, request.session.get('selected_machine_id'))
    has_unsolved_reports = ReportsModel.objects.filter(
        order__related_to_shift=shift, is_solved=False
    ).exists()
    context = {
        'user': request.user,
        'custom_user': custom_user,
        'shift': shift,
        'order': order,
        'has_unsolved_reports': has_unsolved_reports
    }
    if request.method == 'POST':
        if 'back' in request.POST:
            machine_free(order, 'in_progress')
            order.delete()
            return redirect('shift_main_page')
        part_name = request.POST.get('partname')
        add_part_name(order, part_name)
        return redirect('shift_qauntity_page')
    return render(request, 'include/shift/scan_name_page.html', context)


def order_qauntity_view(request):
    custom_user = CustomUserModel.objects.filter(user=request.user.id).last()
    shift = get_last_or_create_shift(custom_user)
    order = get_order(custom_user, shift, request.session.get('selected_machine_id'))
    has_unsolved_reports = ReportsModel.objects.filter(
        order__related_to_shift=shift, is_solved=False
    ).exists()
    context = {
        'user': request.user,
        'custom_user': custom_user,
        'shift': shift,
        'order': order,
        'has_unsolved_reports': has_unsolved_reports
    }

    if request.method == 'POST':
        if 'pause_shift' in request.POST:  # Обработка кнопки "Приостановить работу/перейти к другому станку"
            set_on_hold(request, order)
            return redirect('shift_main_page')
        quantity = int(request.POST.get('quantity'))
        add_quantity(order, quantity)
        add_start_working_time(order)
        return redirect('shift_setup_page')

    return render(request, 'include/shift/quantity_page.html', context)


def order_setup_view(request):
    custom_user = CustomUserModel.objects.filter(user=request.user.id).last()
    shift = get_last_or_create_shift(custom_user)
    order = get_order(custom_user, shift, request.session.get('selected_machine_id'))
    has_unsolved_reports = ReportsModel.objects.filter(
        order__related_to_shift=shift, is_solved=False
    ).exists()
    context = {
        'user': request.user,
        'custom_user': custom_user,
        'shift': shift,
        'order': order,
        'has_unsolved_reports': has_unsolved_reports
    }
    if request.method == 'POST':
        if 'pause_shift' in request.POST:  # Обработка кнопки "Приостановить работу/перейти к другому станку"
            set_on_hold(request, order)
            return redirect('shift_main_page')
        add_machine_start_time(order)
        return redirect('shift_processing_page')
    return render(request, 'include/shift/setup_page.html', context)


def order_processing_view(request):
    custom_user = CustomUserModel.objects.filter(user=request.user.id).last()
    shift = get_last_or_create_shift(custom_user)
    order = get_order(custom_user, shift, request.session.get('selected_machine_id'))
    has_unsolved_reports = ReportsModel.objects.filter(
        order__related_to_shift=shift, is_solved=False
    ).exists()
    context = {
        'user': request.user,
        'custom_user': custom_user,
        'shift': shift,
        'order': order,
        'has_unsolved_reports': has_unsolved_reports
    }
    if request.method == 'POST':
        if 'pause_shift' in request.POST:  # Обработка кнопки "Приостановить работу/перейти к другому станку"
            set_on_hold(request, order)
            return redirect('shift_main_page')
        add_machine_end_time(order)
        return redirect('shift_ending_page')
    return render(request, 'include/shift/processing_page.html', context)



def order_ending_view(request):
    custom_user = CustomUserModel.objects.filter(user=request.user.id).last()
    shift = get_last_or_create_shift(custom_user)
    order = get_order(custom_user, shift, request.session.get('selected_machine_id'))
    has_unsolved_reports = ReportsModel.objects.filter(
        order__related_to_shift=shift, is_solved=False
    ).exists()
    context = {
        'user': request.user,
        'custom_user': custom_user,
        'shift': shift,
        'order': order,
        'has_unsolved_reports': has_unsolved_reports
    }
    if request.method == 'POST':
        if 'pause_shift' in request.POST:  # Обработка кнопки "Приостановить работу/перейти к другому станку"
            set_on_hold(request, order)
            return redirect('shift_main_page')
        add_end_working_time(order)
        machine_free(order)
        count_and_set_reports_duration(order)
        return redirect('shift_main_page')
    return render(request, 'include/shift/ending_order_page.html', context)


def report_send(request):
    custom_user = CustomUserModel.objects.get(id=request.user.id)
    shift = get_last_or_create_shift(custom_user)
    order = get_order(custom_user, shift, request.session.get('selected_machine_id'))
    if request.method == 'POST':
        add_report(request, order, custom_user)
        return HttpResponse('Report sent successfully')
    else:
        return HttpResponse('Bad request')


def reports_view(request):
    custom_user = CustomUserModel.objects.get(id=request.user.id)
    user_reports = ReportsModel.objects.filter(user=custom_user).order_by('-start_time').order_by('is_solved')
    form = ReportEditForm()

    context = {
        'user_reports': user_reports,
        'form': form,
        'custom_user': custom_user
    }
    # POST to solve report and set is_broken False
    if request.method == 'POST':
        report_id = request.POST.get('bug_id')
        report = get_object_or_404(ReportsModel, pk=report_id)
        form = ReportEditForm(request.POST, instance=report)
        if form.is_valid():
            if form.cleaned_data['is_solved']:
                report.end_time = timezone.now()
            form.save()
            machine_free(report.order, status='broken')
            return JsonResponse({'status': 'success'})
    return render(request, 'include/reports_page.html' , context)


def request_send(request):
    custom_user = CustomUserModel.objects.get(id=request.user.id)
    if request.method == 'POST':
        add_request(request, custom_user)
        return HttpResponse('Request sent successfully')
    else:
        return HttpResponse('Bad request')








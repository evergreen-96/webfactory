from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from core.buisness import *
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
    context = {
        'user': request.user,
        'custom_user': custom_user,
        'machines': machines
    }
    if request.method == 'POST':
        selected_machine_id = request.POST.get('selected_machine_id')
        request.session['selected_machine_id'] = selected_machine_id
        if 'continue' in request.POST:
            order = get_order(custom_user, shift, selected_machine_id)
            remove_hold(order)
            return redirect(order.hold_url)
        if 'start_new' in request.POST:
            start_new_order(custom_user, shift, selected_machine_id)
            return redirect('shift_scan_page')
        if 'stop_working' in request.POST:
            order = get_order(custom_user, shift, selected_machine_id)
            stop_order(order)
            return redirect('shift_main_page')
        if 'end_shift' in request.POST:
            # TODO: add buisness logic!
            return redirect('shift_main_page')
    return render(request, 'include/shift/main_page.html', context)


def shift_scan_view(request):
    custom_user = CustomUserModel.objects.get(id=request.user.id)
    shift = get_last_or_create_shift(custom_user)
    order = get_order(custom_user, shift, request.session.get('selected_machine_id'))
    if request.method == 'POST':
        part_name = request.POST.get('partname')
        add_part_name(order, part_name)
        return redirect('shift_qauntity_page')
    return render(request, 'include/shift/scan_name_page.html')


def shift_qauntity_view(request):
    custom_user = CustomUserModel.objects.get(id=request.user.id)
    shift = get_last_or_create_shift(custom_user)
    order = get_order(custom_user, shift, request.session.get('selected_machine_id'))

    if request.method == 'POST':
        if 'pause_shift' in request.POST:  # Обработка кнопки "Приостановить работу/перейти к другому станку"
            set_on_hold(request, order)
            return redirect('shift_main_page')
        quantity = int(request.POST.get('quantity'))
        add_quantity(order, quantity)
        add_start_working_time(order)
        return redirect('shift_setup_page')

    return render(request, 'include/shift/quantity_page.html')


def shift_setup_view(request):
    custom_user = CustomUserModel.objects.get(id=request.user.id)
    shift = get_last_or_create_shift(custom_user)
    order = get_order(custom_user, shift, request.session.get('selected_machine_id'))
    if request.method == 'POST':
        print(request.POST)
        if 'pause_shift' in request.POST:  # Обработка кнопки "Приостановить работу/перейти к другому станку"
            set_on_hold(request, order)
            return redirect('shift_main_page')
        add_machine_start_time(order)
        return redirect('shift_processing_page')
    return render(request, 'include/shift/setup_page.html')


def shift_processing_view(request):
    custom_user = CustomUserModel.objects.get(id=request.user.id)
    shift = get_last_or_create_shift(custom_user)
    order = get_order(custom_user, shift, request.session.get('selected_machine_id'))
    if request.method == 'POST':
        if 'pause_shift' in request.POST:  # Обработка кнопки "Приостановить работу/перейти к другому станку"
            set_on_hold(request, order)
            return redirect('shift_main_page')
        add_machine_end_time(order)
        return redirect('shift_ending_page')
    return render(request, 'include/shift/processing_page.html')


def shift_ending_view(request):
    custom_user = CustomUserModel.objects.get(id=request.user.id)
    shift = get_last_or_create_shift(custom_user)
    order = get_order(custom_user, shift, request.session.get('selected_machine_id'))
    if request.method == 'POST':
        if 'pause_shift' in request.POST:  # Обработка кнопки "Приостановить работу/перейти к другому станку"
            set_on_hold(request, order)
            return redirect('shift_main_page')
        add_end_working_time(order)
        machine_free(order)
        return redirect('shift_main_page')
    return render(request, 'include/shift/ending_order_page.html')


def report_send(request):
    custom_user = CustomUserModel.objects.get(id=request.user.id)
    shift = get_last_or_create_shift(custom_user)
    order = get_order(custom_user, shift, request.session.get('selected_machine_id'))
    if request.method == 'POST':
        add_report(request, order, custom_user)


def reports_view(request, report_id=None):
    return render(request, 'include/reports_page.html', context)


def request_view(request):
    if request.method == 'POST':
        print(request.POST)
    return render(request, 'bugreport_form.html')

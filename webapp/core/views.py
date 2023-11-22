from types import NoneType

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.management import call_command
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from core.buisness import *
from core.decorators import check_bug_solved
from core.forms import BugEditForm
from core.models import CustomUserModel, StatDataModel, UserRequestsModel


def login_view(request):
    """
       Handles the login functionality.
       Parameters:
           request (HttpRequest): The HTTP request object.
       Returns:
           HttpResponse: The HTTP response object.
       Description:
           This function handles the login functionality. It checks if the request method is POST, retrieves the username and password from the request, authenticates the user, and if the authentication is successful, logs in the user and redirects them to the 'main' page. If the authentication fails, it displays an error message. If the request method is not POST, it renders the 'login.html' template.
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

@check_bug_solved
def main_page(request):
    """
    Заглавная страница сайта
    """

    # устанавливает сессию, чтобы нельзя было войти на страницу
    request.session['prev_page'] = True
    request.session['visit'] = 0
    try:
        user_profile = CustomUserModel.objects.filter(user=request.user).last()
        last_order = StatOrdersModel.objects.filter(user=user_profile).last()
        context = {
            'custom_user': user_profile,
            'current_time': timezone.now(),
        }
        shift = StatDataModel.objects.filter(user=user_profile) \
            .filter(shift_end_time__lt=timezone.now()).count()
    except:
        context = {
            'custom_user': None,
            'current_time': timezone.now(),
        }
    #     проверка, чтобы не было более 2х смен за календарный день
    if request.method == 'POST' and shift >= 2:

        return redirect('main')
    # Создаем заготовку для заказа
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

@check_bug_solved
@login_required(login_url='login')
def shift_main_page(request):
    """
    Страница начала смены
    (можно начать новую деталь или закончить смену)
    """
    request.session['prev_page'] = False
    user_profile = CustomUserModel.objects.get(user=request.user)
    shift = StatDataModel.objects.filter(user=user_profile).last()
    users_machines = user_profile.position.machine.all()
    current_time = timezone.now()
    context = {
        'custom_user': user_profile,
        'users_machines': users_machines,
        'current_time': current_time,
    }

    if request.method == 'POST':
        try:
            selected_machine_id = request.POST.get('selected_machine')
            selected_machine = users_machines.get(pk=selected_machine_id)
        except:
            pass
        if 'endShift' not in request.POST:
            create_or_get_last_order(user_profile, shift, selected_machine)
            return redirect('shift_scan')
        elif 'endShift' in request.POST:
            end_shift(shift)
            return redirect('main')

    return render(request, 'include/shift_first_page.html', context)

@check_bug_solved
@login_required(login_url='login')
@csrf_exempt
def shift_scan(request):
    """
    Страница сканирование QR
    """
    user_profile = CustomUserModel.objects.get(user=request.user)
    last_order = StatOrdersModel.objects.filter(user=user_profile).last()
    context = {
        'custom_user': user_profile,
        'current_time': timezone.now(),
        'last_order': last_order
    }
    if request.method == 'POST':
        partname = request.POST.get('partname')
        last_order.part_name = partname
        last_order.order_scan_time = timezone.now()
        last_order.save()
        return redirect('shift_part_qaun')
    return render(request, 'include/shift_scan.html', context)

@check_bug_solved
@login_required(login_url='login')
def shift_part_qaun(request):
    """
    Страница выбора количества деталей
    """
    selected_value = request.POST.get('quantity', '')
    button_value = request.POST.get('button', '')
    selected_button = selected_value if selected_value else button_value
    user_profile = CustomUserModel.objects.get(user=request.user)
    last_order = StatOrdersModel.objects.filter(user=user_profile).last()
    context = {
        'custom_user': user_profile,
        'current_time': timezone.now(),
        'last_order': last_order,
        'selected_value': selected_button
    }
    if request.method == 'POST':
        last_order.num_parts = selected_value
        last_order.order_start_working_time = timezone.now()
        last_order.save()

        return redirect('shift_setup')
    return render(request, 'include/shift_part_qaun.html',
                  context)

@check_bug_solved
@login_required(login_url='login')
def shift_setup(request):
    user_profile = CustomUserModel.objects.get(user=request.user)
    last_order = StatOrdersModel.objects.filter(user=user_profile).last()
    context = {
        'custom_user': user_profile,
        'current_time': timezone.now(),
        'last_order': last_order
    }

    if request.method == 'POST':
        last_order.order_machine_start_time = timezone.now()
        last_order.save()
        return redirect('shift_processing')
    return render(request, 'include/shift_setup.html', context)

@check_bug_solved
@login_required(login_url='login')
def shift_processing(request):
    user_profile = CustomUserModel.objects.get(user=request.user)
    last_order = StatOrdersModel.objects.filter(user=user_profile).last()
    context = {
        'custom_user': user_profile,
        'current_time': timezone.now(),
        'last_order': last_order
    }
    if request.method == 'POST':
        last_order.order_machine_end_time = timezone.now()
        last_order.save()
        return redirect('shift_ending')
    return render(request, 'include/shift_processing.html', context)

@check_bug_solved
@login_required(login_url='login')
def shift_ending(request):
    user_profile = CustomUserModel.objects.get(user=request.user)
    last_order = StatOrdersModel.objects.filter(user=user_profile).last()
    context = {
        'custom_user': user_profile,
        'current_time': timezone.now(),
        'last_order': last_order
    }

    if request.method == 'POST':
        last_order.order_end_working_time = timezone.now()
        last_order.save()
        last_order.order_bugs_time = count_bugs_duration(last_order)
        last_order.save()
        return redirect('shift_main_page')
    return render(request, 'include/shift_ending.html', context)


@login_required(login_url='login')
def error_report(request):
    user_profile = CustomUserModel.objects.get(user=request.user)
    last_order = StatOrdersModel.objects.filter(user=user_profile).last()
    user_reports = StatBugsModel.objects.filter(user=user_profile)
    context = {
        'custom_user': user_profile,
        'users_reports': user_reports
    }

    if request.method == 'POST':
        new_bug = StatBugsModel(
            user=CustomUserModel.objects.get(user=request.user),
            order=last_order,
            bug_description=request.POST.get('bug_description'),
            bug_end_time=None,
            url=request.META.get('HTTP_REFERER', '/'),
        )

        new_bug.save()
    return render(request, 'include/error_report.html', context)


@login_required(login_url='login')
def user_request_view(request):
    user_profile = CustomUserModel.objects.get(user=request.user)
    user_requests = UserRequestsModel.objects.filter(user=user_profile).last()
    context = {
        'custom_user': user_profile,
        'users_reports': user_requests
    }

    if request.method == 'POST':
        new_request = UserRequestsModel(
            user=CustomUserModel.objects.get(user=request.user),
            report_description=request.POST.get('request_description'),
        )
        new_request.save()

    return render(request, 'include/error_report.html', context)


@login_required(login_url='login')
def bug_list(request):
    user = CustomUserModel.objects.get(user=request.user)
    bugs = StatBugsModel.objects.filter(user=user)
    form = BugEditForm()
    last_bug_url = bugs.last().url if bugs.last() else '/'
    context = {
        'bugs': bugs,
        'form': form,
        'user_profile': user,
        'prev_page': last_bug_url
    }
    if request.method == 'POST':
        bug_id = request.POST.get('bug_id')
        bug = get_object_or_404(StatBugsModel, pk=bug_id)
        form = BugEditForm(request.POST, instance=bug)

        if form.is_valid():
            if form.cleaned_data['is_solved']:
                bug.bug_end_time = timezone.now()
            form.save()
            return JsonResponse({'status': 'success'})

    return render(request, 'include/bug_list.html', context)


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser)
def backup(requests):
    filename = timezone.datetime.now().date()  # output filename here
    saveDir = open("./backups/{}.json".format(filename), 'w')

    call_command('dumpdata', 'core', stdout=saveDir, indent=3)
    saveDir.close()
    return HttpResponse(saveDir.name)

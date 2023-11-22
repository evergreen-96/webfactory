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
from core.models import CustomUserModel, ShiftModel, UserRequestsModel


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
            # TODO: add buisness logic!
            return redirect('shift_main_page')
        elif 'logout' in request.POST:
            return redirect('logout')
    return render(request, 'include/shift/pre_shift_page.html', context)


def shift_main_view(request):
    """
    Главная страница смены
    """
    custom_user = CustomUserModel.objects.get(id=request.user.id)
    machines = custom_user.machine.all()
    context = {
        'user': request.user,
        'custom_user': custom_user,
        'machines': machines
    }
    return render(request, 'include/shift/shift_main_page.html', context)


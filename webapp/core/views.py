from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.http import QueryDict, HttpResponse
from django.shortcuts import render, redirect

from core.forms import ProducedForm, RegistrationForm, CustomLoginForm
from core.models import ProducedModel


def produced_model_list(request):
    produced_models = ProducedModel.objects.all()
    return render(request, 'include/content.html', {'produced_models': produced_models,
                                                    'profile': request.user})


def produced_new(request):
    if request.method == 'POST':
        form = ProducedForm(request.POST)
        if form.is_valid():
            form.instance.worker = request.user
            form.save()
    else:
        form = ProducedForm()
    return render(request, 'include/testify_form.html', {'form': form, 'inst': 1,
                                                    'profile': request.user})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        password = form.gen_password()
        if form.is_valid():
            user = form.save()
            user.set_password(raw_password=password)
            user.save()
            return HttpResponse(status=200)
    else:
        form = RegistrationForm()
    return render(request, 'include/register.html', {'form': form,
                                                    'profile': request.user})


def custom_login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('produced_model_list')
    else:
        form = CustomLoginForm()
    return render(request, 'include/login.html', {'form': form,
                                                    'profile': request.user})


def logout_redirect(request):
    return redirect('produced_model_list')

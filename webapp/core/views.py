from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from core.forms import ProducedForm, RegistrationForm, CustomLoginForm
from core.models import ProducedModel


def produced_model_list(request):
    produced_models = ProducedModel.objects.all()
    return render(request, 'include/content.html', {'produced_models': produced_models,
                                                    'profile': request.user})


@login_required
def produced_new(request):
    if request.method == 'POST':
        form = ProducedForm(request.POST)
        if form.is_valid():
            form.instance.worker = request.user
            form.save()
            return redirect('main')

    else:
        form = ProducedForm()
    return render(request, 'include/new_record_form.html', {'form': form, 'inst': 1,
                                                         'profile': request.user})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        password = form.gen_password()
        if form.is_valid():
            user = form.save()
            user.set_password(raw_password=password)
            user.save()
            return redirect('login')
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
                return redirect('main')
    else:
        form = CustomLoginForm()
    return render(request, 'include/login.html', {'form': form,
                                                  'profile': request.user})


def logout_redirect(request):
    return redirect('main')

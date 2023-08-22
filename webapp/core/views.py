from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect

from core.decorators import logout_required
from core.forms import ProducedForm, RegistrationForm, CustomLoginForm, \
    CustomResetPassForm
from core.models import ProducedModel




def produced_view(request):
    produced_models = ProducedModel.objects.all()
    return render(request, 'include/content.html', {'produced_models': produced_models,
                                                    'profile': request.user})


@login_required
def produced_new_view(request):
    if request.method == 'POST':
        form = ProducedForm(request.POST)
        if form.is_valid():
            form.instance.worker = request.user
            form.save()
            return redirect('main')
    else:
        form = ProducedForm()
    return render(request, 'forms/new_record_form.html', {'form': form, 'inst': 1,
                                                         'profile': request.user})


def register_view(request):
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


def custom_login_view(request):
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

@logout_required()
def reset_password_view(request):
    if request.method == 'POST':
        form = CustomResetPassForm(request.POST)
        if form.is_valid():
            found_user = User.objects.filter(
                username=form.cleaned_data['username']).first()
            found_user.set_password(
                raw_password=form.cleaned_data['new_password']
            )
            found_user.save()
            return HttpResponse('не проеби хоть этот... Пасс:' + form.cleaned_data['new_password'])
    else:
        form=CustomResetPassForm()
    return render(request, 'include/reset_password.html', {'form':form})

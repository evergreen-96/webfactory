from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from core.models import CustomUserModel, StatBugsModel


def logout_required(function=None, logout_url='logout_redirect'):
    actual_decorator = user_passes_test(
        lambda u: not u.is_authenticated,
        login_url=logout_url
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def check_prev_page(view_func):
    def wrapped(request, *args, **kwargs):
        if not request.session.get('prev_page'):
            return redirect('main')  # Замените 'main_page' на имя вашего URL-маршрута
        return view_func(request, *args, **kwargs)
    return wrapped


def check_bug_solved(view_func):
    def wrapper(request, *args, **kwargs):
        request.session['redirect_from'] = request.get_full_path()
        try:
            user_profile = CustomUserModel.objects.get(user=request.user)
            unsolved_bugs = StatBugsModel.objects.filter(user=user_profile, is_solved=False)
            if unsolved_bugs.exists():
                return redirect('users_bugs')
        except TypeError:
            return view_func(request, *args, **kwargs)
            # Нет нерешенных багов, продолжаем выполнение оригинального представления
        return view_func(request, *args, **kwargs)
    return wrapper
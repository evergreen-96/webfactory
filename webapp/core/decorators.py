from django.conf import settings
from django.contrib.auth.decorators import user_passes_test


def logout_required(function=None, logout_url='logout_redirect'):
    actual_decorator = user_passes_test(
        lambda u: not u.is_authenticated,
        login_url=logout_url
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

from django.shortcuts import redirect

def check_prev_page(view_func):
    def wrapped(request, *args, **kwargs):
        if not request.session.get('prev_page'):
            return redirect('main')  # Замените 'main_page' на имя вашего URL-маршрута
        return view_func(request, *args, **kwargs)
    return wrapped

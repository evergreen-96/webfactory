from django.contrib.auth.views import LogoutView
from django.urls import path

from core.views import produced_view, produced_new_view, register_view, \
    custom_login_view, logout_redirect, reset_password_view

urlpatterns = [
    path('', produced_view, name='main'),
    path('new/', produced_new_view, name='newrecord'),
    path('register/', register_view, name='register'),
    path('login/', custom_login_view, name='login'),
    path('logout-redirect/', logout_redirect, name='logout_redirect'),
    path('logout/', LogoutView.as_view(next_page='logout_redirect'), name='logout'),
    path('reset-password/', reset_password_view, name='reset_pass'),
]

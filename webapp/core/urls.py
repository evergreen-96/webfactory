from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from core.views import produced_model_list, produced_new, register, custom_login, logout_redirect

urlpatterns = [
    path('1/', produced_model_list, name='produced_model_list'),
    path('new/', produced_new, name='produced_new'),
    path('register/', register, name='register'),
    path('login/', custom_login, name='login'),
    path('logout-redirect/', logout_redirect, name='logout_redirect'),
    path('logout/', LogoutView.as_view(next_page='logout_redirect'), name='logout'),

]
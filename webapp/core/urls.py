from django.urls import path

from core.views import produced_model_list, produced_new

urlpatterns = [
    path('1/', produced_model_list, name='produced_model_list'),
    path('new/', produced_new, name='produced_new'),

]
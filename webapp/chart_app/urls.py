from django.contrib import admin
from django.urls import path, include

from chart_app.views import chart_view

urlpatterns = [
    path('', chart_view, name='chart_page'),
]

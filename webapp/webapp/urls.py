"""
URL configuration for webapp project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('api-v1/', include('api_v1.urls')),
    path("__debug__/", include("debug_toolbar.urls")),
]

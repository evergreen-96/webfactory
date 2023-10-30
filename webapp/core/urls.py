from django.contrib.auth.views import LogoutView
from django.urls import path

from core.views import main_page, shift_main_page, shift_scan, shift_part_qaun, shift_setup, decode_photo

urlpatterns =[
    path('', main_page, name='main'),
    path('shift/', shift_main_page, name='shift_main_page'),
    path('qr-decoder/', decode_photo, name='decode_photo'),
    path('shift/scan/', shift_scan, name='shift_scan'),
    path('shift/quantity/', shift_part_qaun, name='shift_part_qaun'),
    path('shift/setup/', shift_setup, name='shift_setup')
]


from django.urls import path

from core.views import main_page, shift_main_page, \
    shift_scan, shift_part_qaun, \
    shift_setup, decode_photo, error_report, shift_processing, shift_ending, \
    login_view, logout_view

urlpatterns = [
    path('', main_page, name='main'),
    path('shift/', shift_main_page, name='shift_main_page'),
    path('report/', error_report, name='error_report'),
    path('qr-decoder/', decode_photo, name='decode_photo'),
    path('shift/scan/', shift_scan, name='shift_scan'),
    path('shift/quantity/', shift_part_qaun, name='shift_part_qaun'),
    path('shift/setup/', shift_setup, name='shift_setup'),
    path('shift/processing/', shift_processing, name='shift_processing'),
    path('shift/ending/', shift_ending, name='shift_ending'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]

from django.urls import path

from core.views import decode_photo, pre_shift_view, login_view, logout_view, shift_main_view

urlpatterns = [
    path('', pre_shift_view, name='main'),
    path('shift/', shift_main_view, name='shift_main_page'),
    # path('report/', error_report, name='error_report'),
    # path('request/', user_request_view, name='user_request'),
    # path('qr-decoder/', decode_photo, name='decode_photo'),
    # path('shift/scan/', shift_scan, name='shift_scan'),
    # path('shift/quantity/', shift_part_qaun, name='shift_part_qaun'),
    # path('shift/setup/', shift_setup, name='shift_setup'),
    # path('shift/processing/', shift_processing, name='shift_processing'),
    # path('shift/ending/', shift_ending, name='shift_ending'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    # path('bug-list/', bug_list, name='users_bugs'),
    # path('backup/', backup, name='backup'),
]

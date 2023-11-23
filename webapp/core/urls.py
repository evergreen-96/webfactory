from django.urls import path

from core.views import decode_photo, pre_shift_view, login_view, logout_view, shift_main_view, shift_scan_view, \
    shift_qauntity_view, shift_setup_view, shift_processing_view, shift_ending_view, report_send, reports_view

urlpatterns = [
    path('', pre_shift_view, name='main'),
    path('shift/', shift_main_view, name='shift_main_page'),
    path('report/', report_send, name='report_page'),
    path('reports/', reports_view, name='reports_view'),
    path('qr-decoder/', decode_photo, name='decode_photo'),
    path('shift/scan/', shift_scan_view, name='shift_scan_page'),
    path('shift/quantity/', shift_qauntity_view, name='shift_qauntity_page'),
    path('shift/setup/', shift_setup_view, name='shift_setup_page'),
    path('shift/processing/', shift_processing_view, name='shift_processing_page'),
    path('shift/ending/', shift_ending_view, name='shift_ending_page'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('reports/', reports_view, name='reports'),
    # path('backup/', backup, name='backup'),

]

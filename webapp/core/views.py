import base64
import io

from PIL import Image
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from core.decorators import logout_required, check_prev_page
from core.models import CustomUserModel, StatDataModel

from pyzbar.pyzbar import decode


@login_required
def main_page(request):
    # устанавливает сессию, чтобы нельзя было войти на страницу
    request.session['prev_page'] = True
    custom_user = CustomUserModel.objects.get(user=request.user)
    current_time = timezone.now()
    context = {
        'custom_user': custom_user,
        'current_time': current_time,
    }
    if request.method == 'POST':
        shift_start_time = timezone.now()
        shift_end_time = None
        num_ended_orders = 0
        shift_time_total = None
        good_time = None
        bad_time = None
        lost_time = None
        total_bugs_time = None
        shift = StatDataModel(
            user=custom_user,
            shift_start_time=shift_start_time,
            shift_end_time=shift_end_time,
            num_ended_orders=num_ended_orders,
            shift_time_total=shift_time_total,
            good_time=good_time,
            bad_time=bad_time,
            lost_time=lost_time,
            total_bugs_time=total_bugs_time,
        )
        # shift.save()
        return redirect('shift_main_page')
    return render(request, 'include/user_inf_start_shift.html', context)


@check_prev_page
def shift_main_page(request):
    request.session['prev_page'] = False
    custom_user = CustomUserModel.objects.get(user=request.user)
    current_time = timezone.now()
    context = {
        'custom_user': custom_user,
        'current_time': current_time,
    }
    return render(request, 'include/shift_first_page.html', context)

def decode_photo(image_data):
    """
    decode image_data
    return :str
    """
    image = Image.open(image_data)
    resized = image.resize((500, 500))
    decoded_qr_img = decode(resized)
    try:
        cropped_data = decoded_qr_img[0].data
        decoded_qr_data = cropped_data.decode('utf-8')
    except IndexError:
        decoded_qr_data = 'Ошибка в декодировании'
    print(decoded_qr_data)
    return decoded_qr_data


@csrf_exempt
def shift_scan(request):
    decoded_qr_data = ""
    if request.method == 'POST':
        image_data = request.FILES.get('image')
        if image_data:
            decoded_qr_data = decode_photo(image_data)
        else:
            part_name = request.POST.get('partname')
            decoded_qr_data = part_name
    return render(request, 'include/shift_scan.html', {'decoded_qr_data': decoded_qr_data})


def shift_part_qaun(request):
    selected_value = request.POST.get('custom_value', '')
    button_value = request.POST.get('button', '')
    selected_button = button_value if button_value else selected_value
    if request.method == 'POST':
        print(selected_button)
    return render(request, 'include/shift_part_qaun.html', {'selected_value': selected_button})
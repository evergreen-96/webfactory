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
    return render(request, 'include/shift_main_page.html', context)

@csrf_exempt
def shift_scan(request):
    if request.method == 'POST':
        image_data = request.body
        # Здесь вы можете обработать видеопоток, полученный от клиента, и попытаться сканировать QR-код.
        # Затем вернуть результат сканирования.
    return render(request, 'include/shift_scan.html')


def endp(request):
    image_data = request.body
    print(123123)
    # Декодируйте данные изображения из base64
    image_data = image_data.decode("utf-8").split(",")[1]
    image_data = base64.b64decode(image_data)
    try:
        image = Image.open(io.BytesIO(image_data))
    except Exception as e:
        # Если возникает ошибка, это может быть из-за некорректных данных изображения
        print(f"Ошибка при открытии изображения: {e}")
    else:
        # Теперь вы можете работать с объектом изображения, например, сохранить его

        image.save('123.png')
    return HttpResponse('endp')

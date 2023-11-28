from datetime import timedelta

from PIL import Image
from django.db.models import Sum, ExpressionWrapper, F, fields
from django.http import HttpResponse
from django.utils import timezone
from pyzbar.pyzbar import decode

from core.models import ReportsModel, OrdersModel, ShiftModel, MachineModel, UserRequestsModel, PositionsModel


def get_last_or_create_shift(custom_user):
    """
    Retrieves the last shift associated with the given custom user.

    Parameters:
        custom_user (CustomUser): The custom user for which to retrieve the last shift.

    Returns:
        ShiftModel: The last shift associated with the custom user.
        If no previous shift exists or the last shift is ended, a new shift is created and returned.
    """
    last_shift = ShiftModel.objects.filter(user=custom_user).last()
    if not last_shift or last_shift.is_ended():
        new_shift = ShiftModel(user=custom_user)
        new_shift.save()
        return new_shift
    else:
        return last_shift


def is_all_orders_ended(shift):
    """
    Проверяет, завершены ли все заказы в указанной смене.
    Возвращает True, если все заказы завершены, иначе False.
    """
    orders = OrdersModel.objects.filter(related_to_shift=shift)
    if not orders:
        return True  # Все заказы завершены, если список пуст
    for order in orders:
        if not order.is_ended():
            return False
    return True


def start_new_order(custom_user, shift, selected_machine):
    machine = MachineModel.objects.get(id=selected_machine)
    machine.is_in_progress = True
    new_order = OrdersModel.objects.create(
        user=custom_user,
        machine=machine,
        related_to_shift=shift,
        start_time=timezone.now()
    )
    machine.order_in_progress = new_order
    machine.save()
    return new_order


def get_order(custom_user, shift, selected_machine):
    order = OrdersModel.objects.filter(
        user=custom_user,
        related_to_shift=shift,
        machine_id=selected_machine
    ).last()
    return order


def stop_order(order):

    machine = MachineModel.objects.get(id=order.machine_id)
    machine.is_in_progress = False
    machine.order_in_progress = None
    order.ended_early = True
    order.end_working_time = timezone.now()
    machine.save()
    order.save()
    return order


def add_part_name(order, part_name):
    order.part_name = part_name
    order.scan_time = timezone.now()
    order.save()
    return order


def add_quantity(order, quantity):
    order.num_parts = quantity
    order.save()
    return order


def add_start_working_time(order):
    order.start_working_time = timezone.now()
    order.save()
    return order


def add_machine_start_time(order):
    order.machine_start_time = timezone.now()
    order.save()
    return order


def add_machine_end_time(order):
    order.machine_end_time = timezone.now()
    order.save()
    return order


def add_end_working_time(order):
    order.end_working_time = timezone.now()
    order.save()
    return order


def machine_free(order, status='in_progress'):
    machine = MachineModel.objects.get(id=order.machine_id)
    if status == 'in_progress':
        machine.order_in_progress = None
        machine.is_in_progress = False
    elif status == 'broken':
        machine.is_broken = False
    elif status == 'both':
        machine.order_in_progress = None
        machine.is_broken = False
        machine.is_in_progress = False
    machine.save()
    return order


def set_on_hold(request, order):
    order.hold_started = timezone.now()
    order.hold_url = request.META.get('HTTP_REFERER', '/')
    order.save()
    return order


def remove_hold(order):
    order.hold_ended = timezone.now()
    order.save()
    return order


def add_report(request, order, custom_user):
    current_url = request.META.get('HTTP_REFERER', '/')
    ReportsModel.objects.create(
        user=custom_user,
        order=order,
        description=request.POST.get('bug_description'),
        start_time=timezone.now(),
        url=current_url
    )
    machine_id = order.machine.id
    machine = MachineModel.objects.get(id=machine_id)
    machine.is_broken = True
    machine.save()

    order.hold_url= current_url
    order.save()


def get_all_reports(user):
    all_reports = ReportsModel.objects.filter(user=user, is_solved=False)
    return all_reports


def add_request(request, custom_user):
    UserRequestsModel.objects.create(
        user=custom_user,
        start_time=timezone.now(),
        description=request.POST.get('request_description')
    )


def count_and_set_reports_duration(order):
    """
    count bugs duration in last order
    return: timedelta
    """
    reports_due_shift = ReportsModel.objects.filter(order=order).filter(
        is_solved=True)
    total_duration = timedelta()
    for report in reports_due_shift:
        one_report_duration = report.end_time - report.start_time
        total_duration += one_report_duration
    order.bugs_time = total_duration
    order.save()
    return total_duration


#
#
def decode_photo(request):
    """
    API endpoint to /qr-decoder/
    decode image_data
    request: request
    return :str
    """
    image_data = request.FILES.get('image')
    image = Image.open(image_data)
    resized = image.resize((500, 500))
    decoded_qr_img = decode(resized)
    try:
        cropped_data = decoded_qr_img[0].data
        decoded_qr_data = cropped_data.decode('utf-8')
    except IndexError:
        decoded_qr_data = 'Ошибка в декодировании'
    return HttpResponse(decoded_qr_data)


def calculate_shift_end_time(shift):
    """
    Время окончания смены
    """
    shift.end_time = timezone.now()
    return shift


def count_num_ended_orders(shift):
    """
    Количество завершенных заказов
    """
    shift.num_ended_orders = OrdersModel.objects.filter(
        related_to_shift=shift, ended_early=False).count()
    return shift


#
#
def calculate_shift_time_total(shift):
    """
    Общее время смены
    """
    shift.time_total = shift.end_time - shift.start_time
    return shift


def calculate_total_bugs_time(shift):
    """
    Общее время багов для каждого заказа внутри смены
    """
    total_bugs_time = OrdersModel.objects.filter(related_to_shift=shift).aggregate(
        total_bugs_time=Sum('bugs_time')
    )['total_bugs_time']
    shift.total_bugs_time = total_bugs_time or timedelta()
    return shift


def calculate_good_time(shift):
    """
    Общее полезное время
    """
    duration_expression = ExpressionWrapper(
        F('machine_end_time') - F('machine_start_time'),
        output_field=fields.DurationField()
    )
    orders = OrdersModel.objects.filter(related_to_shift=shift).exclude(
        machine_end_time__isnull=True
    ).exclude(machine_start_time__isnull=True)

    total_good_time = orders.annotate(
        good_time=Sum(duration_expression, output_field=fields.DurationField())
    ).aggregate(total_good_time=Sum('good_time'))['total_good_time']

    shift.good_time = total_good_time or timedelta()
    return shift


def calculate_bad_time(shift):
    """
    Общее бесполезное время
    """
    total_bad_time = timedelta()

    for order in OrdersModel.objects.filter(related_to_shift=shift):
        if (
            order.end_working_time is not None and
            order.scan_time is not None and
            order.machine_end_time is not None and
            order.machine_start_time is not None and
            order.bugs_time is not None
        ):
            bad_time_in_order = (
                    order.end_working_time - order.scan_time -
                    (order.machine_end_time - order.machine_start_time) -
                    order.bugs_time
            )
            total_bad_time += bad_time_in_order

    if shift.bad_time is not None:
        shift.bad_time += total_bad_time
    else:
        shift.bad_time = total_bad_time

    return shift


def calculate_lost_time(shift):
    """
    Общее потерянное время (рассос)
    """
    chill_time = PositionsModel.objects.get(
        position_name=shift.user.position).chill_time
    total_lost_time = (
            shift.time_total -
            shift.good_time - shift.bad_time -
            shift.total_bugs_time - chill_time
    )
    shift.lost_time = total_lost_time
    return shift


def count_and_end_shift(shift):
    """
    Завершение смены, посчет всего
    """
    try:
        shift = calculate_shift_end_time(shift)
        shift.save()
    except Exception as e:
        print(f'Error in calculate_shift_end_time: {e}')
        return shift

    try:
        shift = count_num_ended_orders(shift)
        shift.save()
    except Exception as e:
        print(f'Error in count_num_ended_orders: {e}')
        return shift

    try:
        shift = calculate_shift_time_total(shift)
        shift.save()
    except Exception as e:
        print(f'Error in calculate_shift_time_total: {e}')
        return shift

    try:
        shift = calculate_total_bugs_time(shift)
        shift.save()
    except Exception as e:
        print(f'Error in calculate_total_bugs_time: {e}')
        return shift

    try:
        shift = calculate_good_time(shift)
        shift.save()
    except Exception as e:
        print(f'Error in calculate_good_time: {e}')
        return shift

    try:
        shift = calculate_bad_time(shift)
        shift.save()
    except Exception as e:
        print(f'Error in calculate_bad_time: {e}')
        return shift

    try:
        shift = calculate_lost_time(shift)
        shift.save()
    except Exception as e:
        print(f'Error in calculate_lost_time: {e}')
        return shift

    return shift


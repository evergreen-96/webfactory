from PIL import Image
from django.http import HttpResponse
from django.utils import timezone
from pyzbar.pyzbar import decode

from core.models import ReportsModel, OrdersModel, ShiftModel, MachineModel


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


def start_new_order(custom_user, shift, selected_machine):
    machine = MachineModel.objects.get(id=selected_machine)
    machine.is_in_progress = True
    machine.save()

    new_order = OrdersModel.objects.create(
        user=custom_user,
        machine=machine,
        related_to_shift=shift,
        start_time=timezone.now()
    )
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


def machine_free(order):
    machine = MachineModel.objects.get(id=order.machine_id)
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
    ReportsModel.objects.create(
        user=custom_user,
        order=order,
        description=request.POST.get('bug_description'),
        start_time=timezone.now(),
        url=request.META.get('HTTP_REFERER', '/')
    )


def get_all_reports(user):
    all_reports = ReportsModel.objects.filter(user=user, is_solved=False)
    return all_reports


def change_report(report_id, is_solved):
    report = ReportsModel.objects.get(id=report_id)
    report.is_solved = bool(is_solved)
    report.save()
    return {'status': 'success'}


######################################################
# def count_bugs_duration(last_order):
#     """
#     count bugs duration in last order
#     return: timedelta
#     """
#     total_bugs = ReportsModel.objects.filter(order=last_order).filter(
#         is_solved=True)
#     total_duration = timedelta()
#
#     for bug in total_bugs:
#         one_bug_duration = bug.end_time - bug.start_time
#         total_duration += one_bug_duration
#     return total_duration
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
#
#
# def create_or_get_last_order(user_profile, shift, selected_machine):
#     # Проверка, если смена не закончилась, то создаем новый заказ, иначе получаем последний
#     if shift.shift_end_time is None:
#         last_order = OrdersModel(
#             user=user_profile,
#             machine=selected_machine,
#             stat_data=shift,
#             part_name='',
#             num_parts=0,
#             order_start_time=None,
#             order_scan_time=None,
#             order_start_working_time=None,
#             order_machine_start_time=None,
#             order_machine_end_time=None,
#             order_end_working_time=None,
#             order_bugs_time=None
#         )
#         last_order.save()
#     else:
#         last_order = OrdersModel.objects.filter(user=user_profile).last()
#
#     last_order.start_time = timezone.now()
#     last_order.save()
#     return last_order
#
#
# def calculate_shift_end_time(shift):
#     """
#     Время окончания смены
#     """
#     shift.shift_end_time = timezone.now()
#     return shift
#
#
# def count_num_ended_orders(shift):
#     """
#     Количество завершенных заказов
#     """
#     shift.num_ended_orders = OrdersModel.objects.filter(
#         stat_data=shift).count()
#     return shift
#
#
# def calculate_shift_time_total(shift):
#     """
#     Общее время смены
#     """
#     shift.time_total = shift.shift_end_time - shift.start_time
#     return shift
#
#
# def calculate_total_bugs_time(shift):
#     """
#     Общее время багов для каждого заказа внутри смены
#     """
#     total_bugs_time = OrdersModel.objects.filter(stat_data=shift).aggregate(
#         total_bugs_time=Sum('bugs_time')
#     )['total_bugs_time']
#     shift.total_bugs_time = total_bugs_time or timedelta()
#     return shift
#
#
# def calculate_good_time(shift):
#     """
#     Общее полезное время
#     """
#     duration_expression = ExpressionWrapper(
#         F('machine_end_time') - F('machine_start_time'),
#         output_field=fields.DurationField()
#     )
#     total_good_time = OrdersModel.objects.filter(stat_data=shift).annotate(
#         good_time=Sum(duration_expression, output_field=fields.DurationField())
#     ).aggregate(total_good_time=Sum('good_time'))['total_good_time']
#     shift.good_time = total_good_time or timedelta()
#     return shift
#
#
# def calculate_bad_time(shift):
#     """
#     Общее бесполезное время
#     """
#     total_bad_time = timedelta()
#
#     for order in OrdersModel.objects.filter(stat_data=shift):
#         bad_time_in_order = (
#                 order.end_working_time - order.scan_time -
#                 (
#                         order.machine_end_time - order.machine_start_time) -
#                 order.bugs_time
#         )
#         total_bad_time += bad_time_in_order
#
#     shift.bad_time = total_bad_time
#     return shift
#
#
# def calculate_lost_time(shift):
#     """
#     Общее потерянное время (рассос)
#     """
#     chill_time = PositionsModel.objects.get(
#         position_name=shift.user.position).chill_time
#     total_lost_time = (
#             shift.time_total -
#             shift.good_time - shift.bad_time -
#             shift.total_bugs_time - chill_time
#     )
#     shift.lost_time = total_lost_time
#     return shift
#
#
# def end_shift(shift):
#     """
#     Завершение смены, посчет всего
#     """
#     try:
#         shift = calculate_shift_end_time(shift)
#         shift = count_num_ended_orders(shift)
#         shift = calculate_shift_time_total(shift)
#         shift = calculate_total_bugs_time(shift)
#         shift = calculate_good_time(shift)
#         shift = calculate_bad_time(shift)
#         shift = calculate_lost_time(shift)
#         shift.save()
#     except TypeError as e:
#         print(f'!!! - {e} !!!')
#         shift.delete()

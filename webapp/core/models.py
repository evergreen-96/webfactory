from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

User = get_user_model()


class MachineTypesModel(models.Model):
    machine_type = models.CharField(max_length=512)

    def __str__(self):
        return self.machine_type


class MachineModel(models.Model):
    machine_type = models.ForeignKey(MachineTypesModel, on_delete=models.CASCADE)
    machine_name = models.CharField(max_length=512)

    def __str__(self):
        return f'{self.machine_name} | Тип: {self.machine_type}'


class RoleModel(models.Model):
    role_name = models.CharField(
        choices=[('worker', 'worker'), ('admin', 'admin')], max_length=64)

    def __str__(self):
        return self.role_name


class WorkingAreaModel(models.Model):
    area_name = models.CharField(max_length=128)

    def __str__(self):
        return self.area_name


class PositionsModel(models.Model):
    position_name = models.CharField(max_length=128)
    chill_time = models.DurationField(max_length=128)
    machine = models.ForeignKey(MachineModel, on_delete=models.CASCADE)

    def __str__(self):
        return self.position_name


class CustomUserModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=64, unique=True)
    role = models.ForeignKey(RoleModel, on_delete=models.CASCADE)
    position = models.ForeignKey(PositionsModel, on_delete=models.CASCADE)
    working_area = models.ForeignKey(WorkingAreaModel,
                                     on_delete=models.CASCADE)


    def __str__(self):
        return self.user.username


class StatDataModel(models.Model):
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    shift_start_time = models.DateTimeField(auto_now_add=True, editable=True)
    shift_end_time = models.DateTimeField(blank=True, null=True)
    num_ended_orders = models.PositiveIntegerField(default=0)
    shift_time_total = models.DurationField(blank=True, null=True)
    good_time = models.DurationField(blank=True, null=True)
    bad_time = models.DurationField(blank=True, null=True)
    lost_time = models.DurationField(blank=True, null=True)
    total_bugs_time = models.DurationField(blank=True, null=True)


    def __str__(self):
        return f'{self.shift_start_time} | {self.user}'


    def is_ended(self):
        return self.shift_end_time is not None

class StatOrdersModel(models.Model):
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    stat_data = models.ForeignKey(StatDataModel, related_name='stat_orders', on_delete=models.CASCADE)
    part_name = models.CharField(max_length=256)
    num_parts = models.PositiveIntegerField()
    order_start_time = models.DateTimeField(blank=True, null=True)
    order_scan_time = models.DateTimeField(blank=True, null=True)
    order_start_working_time = models.DateTimeField(blank=True, null=True)
    order_machine_start_time = models.DateTimeField(blank=True, null=True)
    order_machine_end_time = models.DateTimeField(blank=True, null=True)
    order_end_working_time = models.DateTimeField(blank=True, null=True)
    order_bugs_time = models.DurationField(blank=True, null=True)
    order_on_hold_time = models.DurationField(default='00:00:00')


    def __str__(self):
        return f'{self.order_start_time} | {self.user} | ' \
               f'{self.part_name} - {self.num_parts}'


    def is_ended(self):
        return self.order_end_working_time is not None


class StatBugsModel(models.Model):
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    order = models.ForeignKey(StatOrdersModel, on_delete=models.CASCADE,
                              null=True, blank=True)
    bug_description = models.CharField(max_length=1028)
    bug_start_time = models.DateTimeField(auto_now_add=True)
    bug_end_time = models.DateTimeField(blank=True, null=True)
    is_solved = models.BooleanField(default=False)
    url = models.CharField(max_length=128)


    def __str__(self):
        is_solved = 'Открыт'
        if self.is_solved:
            is_solved = 'Закрыт'
        return f'{self.bug_start_time.date()} | {self.bug_description} | {is_solved}'


class UserRequestsModel(models.Model):
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    report_description = models.CharField(max_length=1028)
    report_start_time = models.DateTimeField(auto_now_add=True)
    report_end_time = models.DateTimeField(blank=True, null=True)
    is_solved = models.BooleanField(default=False)


    def __str__(self):
        is_solved = 'Открыт'
        if self.is_solved:
            is_solved = 'Закрыт'
        return f'{self.report_start_time.date()} | {self.report_description} | {is_solved}'



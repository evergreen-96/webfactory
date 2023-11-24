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
    is_broken = models.BooleanField(default=False)
    is_in_progress = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.machine_name} | Тип: {self.machine_type} | Сломан: {self.is_broken} | В процессе: {self.is_in_progress}'


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

    def __str__(self):
        return self.position_name


class CustomUserModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=64, unique=True)
    role = models.ForeignKey(RoleModel, on_delete=models.CASCADE)
    position = models.ForeignKey(PositionsModel, on_delete=models.CASCADE)
    working_area = models.ForeignKey(WorkingAreaModel,
                                     on_delete=models.CASCADE)
    machine = models.ManyToManyField(MachineModel, blank=True)


    def __str__(self):
        return self.user.username


class ShiftModel(models.Model):
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True, editable=True)
    end_time = models.DateTimeField(blank=True, null=True)
    num_ended_orders = models.PositiveIntegerField(default=0)
    time_total = models.DurationField(blank=True, null=True)
    good_time = models.DurationField(blank=True, null=True)
    bad_time = models.DurationField(blank=True, null=True)
    lost_time = models.DurationField(blank=True, null=True)
    total_bugs_time = models.DurationField(blank=True, null=True)


    def __str__(self):
        return f'{self.start_time} | {self.user}'


    def is_ended(self):
        return self.end_time is not None


class OrdersModel(models.Model):
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    machine = models.ForeignKey(MachineModel, on_delete=models.CASCADE, blank=True, null=True)
    related_to_shift = models.ForeignKey(ShiftModel, related_name='stat_orders', on_delete=models.CASCADE)
    part_name = models.CharField(max_length=256)
    num_parts = models.PositiveIntegerField(default=0)
    start_time = models.DateTimeField(blank=True, null=True)
    scan_time = models.DateTimeField(blank=True, null=True)
    start_working_time = models.DateTimeField(blank=True, null=True)
    machine_start_time = models.DateTimeField(blank=True, null=True)
    machine_end_time = models.DateTimeField(blank=True, null=True)
    end_working_time = models.DateTimeField(blank=True, null=True)
    bugs_time = models.DurationField(blank=True, null=True)
    ended_early = models.BooleanField(default=False)
    hold_started = models.DateTimeField(blank=True, null=True)
    hold_url = models.CharField(max_length=256, blank=True, null=True)
    hold_ended = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return f'{self.id} |{self.related_to_shift.id} {self.user} | ' \
               f'{self.part_name} - {self.num_parts}'


    def is_ended(self):
        return self.end_working_time is not None


class ReportsModel(models.Model):
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    order = models.ForeignKey(OrdersModel, on_delete=models.CASCADE,
                              null=True, blank=True)
    description = models.CharField(max_length=1028)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    is_solved = models.BooleanField(default=False)
    url = models.CharField(max_length=128)


    def __str__(self):
        is_solved = 'Открыт'
        if self.is_solved:
            is_solved = 'Закрыт'
        return f'{self.start_time.date()} | {self.order.related_to_shift.id} | {is_solved}'


class UserRequestsModel(models.Model):
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    description = models.CharField(max_length=1028)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    is_solved = models.BooleanField(default=False)


    def __str__(self):
        is_solved = 'Открыт'
        if self.is_solved:
            is_solved = 'Закрыт'
        return f'{self.start_time.date()} | {self.description} | {is_solved}'



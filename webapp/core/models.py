from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class BuildingModel(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=256, blank=True)


class ToolModel(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=256, blank=True)


class WorkZoneModel(models.Model):
    name = models.CharField(max_length=128)
    building = models.ForeignKey(BuildingModel, on_delete=models.CASCADE)
    tool = models.ForeignKey(ToolModel, on_delete=models.CASCADE)


User = get_user_model()


class ProducedModel(models.Model):
    worker = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    working_zome = models.ForeignKey(WorkZoneModel, on_delete=models.CASCADE)
    total_parts_produced = models.PositiveIntegerField()
    comments = models.CharField(max_length=1080, blank=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(default=timezone.now)
    for_last_hour = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Автоматически вычисляем start_time = end_time - 1 час
        if self.for_last_hour:
            self.start_time = self.end_time - timedelta(hours=1)
        super(ProducedModel, self).save(*args, **kwargs)

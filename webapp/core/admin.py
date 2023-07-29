from django.contrib import admin

from core.models import *

admin.site.register(BuildingModel)
admin.site.register(ToolModel)
admin.site.register(WorkZoneModel)
admin.site.register(ProducedModel)
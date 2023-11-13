from django.contrib import admin


from core.models import *

admin.site.register(RoleModel)
admin.site.register(WorkingAreaModel)
admin.site.register(PositionsModel)
admin.site.register(CustomUserModel)
admin.site.register(StatDataModel)
admin.site.register(StatOrdersModel)
admin.site.register(StatBugsModel)
admin.site.register(UserRequestsModel)

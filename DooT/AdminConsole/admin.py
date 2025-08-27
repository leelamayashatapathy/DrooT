from django.contrib import admin
from .models import AdminProfile,SystemMaintenance,SystemSettings

admin.site.register(AdminProfile)
admin.site.register(SystemSettings)
admin.site.register(SystemMaintenance)  
# Register your models here.

from django.contrib import admin
from solo.admin import SingletonModelAdmin


from .models import DominiosEmail, EmailConfiguration

# Register your models here.

admin.site.register(DominiosEmail)
admin.site.register(EmailConfiguration, SingletonModelAdmin)

from django.contrib import admin

from .models import Canal, Industria


# Register your models here.


class IndustriAdmin(admin.ModelAdmin):
    list_display = ['nombre','descripcion']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by("nombre")


admin.site.register(Canal)
admin.site.register(Industria, IndustriAdmin)

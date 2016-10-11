from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from productos.models import UnidadMedida,Producto
# Register your models here.
class ProductoAdmin(ImportExportModelAdmin):


    def get_queryset(self, request):
        qs = Producto.objects.select_related(
            "margen__proveedor__moneda__moneda_cambio",
            "unidad_medida",
            "margen__categoria",
        ).all()
        return qs

    list_display = (
        'referencia',
        'descripcion_estandar',
        'unidad_medida',
        'margen',
        'costo',
        'get_moneda',
        'get_cambio_moneda',
        'get_factor_importacion',
        'costo_cop',
        'get_margen',
        'precio_base',
        'activo',
        'activo_ensamble',
        'activo_proyectos',
        'activo_componentes',
        'activo_catalogo',
    )
    search_fields = ['referencia','descripcion_estandar']
    list_filter = ('margen__proveedor','margen__categoria','activo','activo_ensamble','activo_proyectos','activo_componentes','activo_catalogo')
    list_editable = ['activo','activo_ensamble','activo_proyectos','activo_componentes','activo_catalogo','margen','costo']
    raw_id_fields = ('margen',)
    readonly_fields = ("precio_base","costo_cop")

    def get_margen(self, obj):
        if obj.margen:
            return obj.margen.margen_deseado
        else:
            return ""
    get_margen.short_description = 'Mgn.'

    def get_factor_importacion(self, obj):
        if obj.margen:
            return obj.margen.proveedor.factor_importacion
        else:
            return ""
    get_factor_importacion.short_description = 'Fac. Imp'

    def get_cambio_moneda(self, obj):
        if obj.margen:
            return obj.margen.proveedor.moneda.moneda_cambio.cambio
        else:
            return ""
    get_cambio_moneda.short_description = 'Tasa'

    def get_moneda(self, obj):
        if obj.margen:
            return obj.margen.proveedor.moneda.moneda_cambio
        else:
            return ""
    get_moneda.short_description = 'Moneda'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        else:
            obj.updated_by = request.user
        obj.save()

admin.site.register(UnidadMedida)
admin.site.register(Producto,ProductoAdmin)
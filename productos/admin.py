from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from productos.models import (
    Producto,
    ArticuloCatalogo
)

class ArticuloCatalogoAdmin(ImportExportModelAdmin):
    list_select_related = (
        'margen',
        'margen__proveedor',
        'margen__categoria',
        'margen__proveedor__moneda',
        'fabricante'
    )

    list_filter = (
        'margen__proveedor', 'activo', 'fabricante__nombre')

    search_fields = [
        'referencia',
        'nombre',
        'fabricante__nombre',
    ]

    list_display = (
        'referencia',
        'nombre',
        'get_fabricante',
        'margen',
        'costo',
        'get_moneda',
        'get_cambio_moneda',
        'get_factor_importacion',
        'get_costo_cop',
        'get_margen',
        'get_precio_base',
        'get_rentabilidad',
        'activo',
    )

    list_editable = ['activo','margen','costo',]
    raw_id_fields = ('margen',)
    readonly_fields = ("get_precio_base", "get_costo_cop", "get_rentabilidad")

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
            return obj.margen.proveedor.moneda.cambio
        else:
            return ""

    get_cambio_moneda.short_description = 'Tasa'

    def get_moneda(self, obj):
        if obj.margen:
            return obj.margen.proveedor.moneda
        else:
            return ""

    get_moneda.short_description = 'Moneda'

    def get_fabricante(self, obj):
        if obj.fabricante:
            return obj.fabricante.nombre
        else:
            return ""

    get_fabricante.short_description = 'Fabricante'

    def get_costo_cop(self, obj):
        return obj.get_costo_cop()
    get_costo_cop.short_description = 'Costo Cop'

    def get_precio_base(self, obj):
        return obj.get_precio_base()
    get_precio_base.short_description = 'Precio Base'

    def get_rentabilidad(self, obj):
        return obj.get_rentabilidad()
    get_rentabilidad.short_description = 'Rentabilidad'

admin.site.register(ArticuloCatalogo,ArticuloCatalogoAdmin)

# region Productos

# region Action Productos
def activar_seleccionados(modeladmin, request, queryset):
    queryset.update(activo=True)


activar_seleccionados.short_description = "Activar Seleccionados"


def activar_seleccionados_componentes(modeladmin, request, queryset):
    queryset.update(activo_componentes=True)


activar_seleccionados_componentes.short_description = "Activar en Componentes"


def activar_seleccionados_proyectos(modeladmin, request, queryset):
    queryset.update(activo_proyectos=True)


activar_seleccionados_proyectos.short_description = "Activar en Proyectos"


def activar_seleccionados_catalogo(modeladmin, request, queryset):
    queryset.update(activo_catalogo=True)


activar_seleccionados_catalogo.short_description = "Activar en Catalogo"


def activar_seleccionados_ensamble(modeladmin, request, queryset):
    queryset.update(activo_ensamble=True)


activar_seleccionados_ensamble.short_description = "Activar en Ensamble Bandas"


# endregion

class ProductoAdmin(ImportExportModelAdmin):
    fieldsets = (
        ('Informacion General', {
            'classes': ('form-control',),
            'fields':
                (
                    ('id_cguno', 'referencia'),
                    'fabricante', 'serie',
                    'descripcion_estandar',
                    'descripcion_comercial',
                    ('con_nombre_automatico'),
                    'foto_perfil'
                )
        }),
        ('Caracteristicas Físicas', {
            'classes': ('form-control',),
            'fields':
                (
                    ('categoria_dos_por_categoria', 'tipo_por_categoria'),
                    ('material', 'color'),
                    ('ancho', 'alto'),
                    ('costo', 'margen'),
                    ('longitud', 'diametro'),
                    ('cantidad_empaque', 'cantidad_minima_venta', 'unidad_medida'),

                )
        }),
        ('Visualización', {
            'classes': ('form-control',),
            'fields':
                (
                    'activo',
                    ('activo_componentes', 'activo_proyectos', 'activo_catalogo', 'activo_ensamble'),
                )
        })
    )

    actions = [
        activar_seleccionados,
        activar_seleccionados_componentes,
        activar_seleccionados_proyectos,
        activar_seleccionados_catalogo,
        activar_seleccionados_ensamble
    ]

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field)
        return obj

    list_select_related = (
        "unidad_medida",
        'margen',
        'margen__proveedor',
        'margen__categoria',
        'margen__proveedor__moneda',
        'categoria_dos_por_categoria',
    )

    list_display = (
        'referencia',
        'id_cguno',
        'descripcion_estandar',
        'unidad_medida',
        'margen',
        'costo',
        'get_moneda',
        'get_cambio_moneda',
        'get_factor_importacion',
        'get_costo_cop',
        'get_margen',
        'get_precio_base',
        'get_rentabilidad',
        'activo',
        'activo_ensamble',
        'activo_proyectos',
        'activo_componentes',
        'activo_catalogo'
    )
    search_fields = [
        'referencia',
        'descripcion_estandar',
        'descripcion_comercial',
        'color__nombre',
        'material__nombre',
        'serie__nombre',
        'fabricante__nombre',
        'categoria_dos_por_categoria__categoria_uno__nombre',
        'categoria_dos_por_categoria__categoria_dos__nombre',
        'tipo_por_categoria__tipo__nombre',
    ]
    list_filter = (
        'margen__proveedor', 'margen__categoria', 'activo', 'activo_ensamble', 'activo_proyectos', 'activo_componentes',
        'activo_catalogo', 'serie')

    list_editable = ['activo', 'activo_ensamble', 'activo_proyectos', 'activo_componentes', 'activo_catalogo', 'margen',
                     'costo', 'id_cguno']
    raw_id_fields = ('margen',)
    readonly_fields = ("precio_base", "costo_cop", "rentabilidad")

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
            return obj.margen.proveedor.moneda.cambio
        else:
            return ""

    get_cambio_moneda.short_description = 'Tasa'

    def get_moneda(self, obj):
        if obj.margen:
            return obj.margen.proveedor.moneda
        else:
            return ""

    get_moneda.short_description = 'Moneda'

    def get_costo_cop(self, obj):
        return obj.get_costo_cop()
    get_costo_cop.short_description = 'Costo Cop'

    def get_precio_base(self, obj):
        return obj.get_precio_base()
    get_precio_base.short_description = 'Precio Base'

    def get_rentabilidad(self, obj):
        return obj.get_rentabilidad()
    get_rentabilidad.short_description = 'Rentabilidad'

    def save_model(self, request, obj, form, change):
        obj.get_nombre_automatico('estandar')
        obj.get_nombre_automatico('comercial')
        if not change:
            obj.created_by = request.user
        else:
            obj.updated_by = request.user
        obj.save()


# endregion
admin.site.register(Producto, ProductoAdmin)

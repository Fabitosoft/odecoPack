from django.db import models


# Create your models here.
# region Categorias Producto
class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    nomenclatura = models.CharField(max_length=3, unique=True)

    class Meta:
        verbose_name_plural = "Categorías Productos"
        verbose_name = "Categoría Producto"

    def __str__(self):
        return self.nombre
# endregion


# region Nombre Estandar
class ProductoNombreConfiguracion(models.Model):
    categoria = models.OneToOneField(CategoriaProducto, on_delete=models.CASCADE, verbose_name='categoría',
                                     related_name='mi_configuracion_producto_nombre_estandar', unique=True)
    con_categoría_uno = models.BooleanField(default=False)
    con_categoría_dos = models.BooleanField(default=False)
    con_serie = models.BooleanField(default=False)
    con_fabricante = models.BooleanField(default=False)
    con_tipo = models.BooleanField(default=False)
    con_material = models.BooleanField(default=False)
    con_color = models.BooleanField(default=False)
    con_ancho = models.BooleanField(default=False)
    con_alto = models.BooleanField(default=False)
    con_longitud = models.BooleanField(default=False)
    con_diametro = models.BooleanField(default=False)

    def __str__(self):
        return self.categoria.nombre

    class Meta:
        verbose_name_plural = 'Configuración Nombres Automáticos'
        verbose_name_plural = 'Configuración Nombre Automático'

# endregion

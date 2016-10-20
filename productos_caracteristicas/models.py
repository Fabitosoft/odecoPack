from django.db import models

# Create your models here.

# region Colores Producto
class ColorProducto(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    nomenclatura = models.CharField(max_length=2, unique=True)

    class Meta:
        verbose_name_plural = "Colores Productos"
        verbose_name = "Color Producto"

    def __str__(self):
        return self.nombre


# endregion

# region Materiales Producto
class MaterialProducto(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    nomenclatura = models.CharField(max_length=2, unique=True)

    class Meta:
        verbose_name_plural = "Materiales Productos"
        verbose_name = "Material Producto"

    def __str__(self):
        return self.nombre


# endregion

# region Series Producto
class SerieProducto(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    nomenclatura = models.CharField(max_length=6, unique=True)

    class Meta:
        verbose_name_plural = "Series Productos"
        verbose_name = "Serie Producto"

    def __str__(self):
        return self.nombre


# endregion

#  region Fabricante Producto
class FabricanteProducto(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    nomenclatura = models.CharField(max_length=2, unique=True)

    class Meta:
        verbose_name_plural = "Fabricantes Productos"
        verbose_name = "Fabricante Producto"

    def __str__(self):
        return self.nombre


# endregion

# region Unidades de Medida
class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    nomenclatura = models.CharField(max_length=2, unique=True)

    class Meta:
        verbose_name_plural = "Unidades de Medida"

    def __str__(self):
        return self.nombre


# endregion

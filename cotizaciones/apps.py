from django.apps import AppConfig


class CotizacionesConfig(AppConfig):
    name = 'cotizaciones'

    def ready(self):
        import cotizaciones.signals
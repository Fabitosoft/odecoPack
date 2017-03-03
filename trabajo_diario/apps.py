from django.apps import AppConfig


class TrabajoDiarioConfig(AppConfig):
    name = 'trabajo_diario'

    def ready(self):
        import trabajo_diario.signals

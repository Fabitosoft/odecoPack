from django.apps import AppConfig


class BandasConfig(AppConfig):
    name = 'bandas'
    verbose_name = 'PRODUCTOS 4 - Bandas'

    def ready(self):
        import bandas.signals

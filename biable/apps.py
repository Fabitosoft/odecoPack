from django.apps import AppConfig


class BiableConfig(AppConfig):
    name = 'biable'

    def ready(self):
        import biable.signals

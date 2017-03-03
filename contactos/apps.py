from django.apps import AppConfig

class ContactosConfig(AppConfig):
    name = 'contactos'

    def ready(self):
        import contactos.signals
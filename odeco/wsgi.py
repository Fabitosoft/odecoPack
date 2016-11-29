"""
WSGI config for odeco project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "odeco.settings")

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

#application = get_wsgi_application()


# <IfModule reqtimeout_module>
#   RequestReadTimeout header=62,MinRate=500 body=62,MinRate=500
# </IfModule>

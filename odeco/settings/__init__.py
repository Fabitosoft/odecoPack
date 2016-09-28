from .base import *
import os

try:
    if os.environ['DJANGO_IS_PRODUCTION']:
        from .production import *
except:
    from .local import *
    print('entro local')
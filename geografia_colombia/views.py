from django.shortcuts import render
from dal import autocomplete
# Create your views here.
from .models import Ciudad
class CiudadAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Ciudad.objects.none()

        qs = Ciudad.objects.all()

        if self.q:
            qs = qs.filter(nombre__istartswith=self.q)

        return qs
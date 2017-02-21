from .models import Colaborador


class UsuariosMixin(object):
    def get_sub_alternos(self, usuario):
        subalternos = Colaborador.objects.values('usuario__user').filter(jefe__usuario__user=usuario)
        return subalternos

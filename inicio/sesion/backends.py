from .models import Registrarse

class MySQLBackend:
    def authenticate(self, request, username=None, password=None):
        try:
            usuario = Registrarse.objects.get(nombre_usuario=username)
            if usuario.contraseña == password:
                return usuario
        except Registrarse.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Registrarse.objects.get(pk=user_id)
        except Registrarse.DoesNotExist:
            return None

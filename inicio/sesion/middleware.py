from django.utils import timezone
from .models import Perfil

class UpdateActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            perfil, created = Perfil.objects.get_or_create(user=request.user)
            perfil.ultima_actividad = timezone.now()
            perfil.save()
        response = self.get_response(request)
        return response

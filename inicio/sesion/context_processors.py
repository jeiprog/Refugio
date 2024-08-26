from django.utils import timezone
from .models import Perfil

def user_online_status(request):
    context = {}
    if request.user.is_authenticated:
        perfil, created = Perfil.objects.get_or_create(user=request.user)
        now = timezone.now()
        if perfil.ultima_actividad and perfil.ultima_actividad > now - timezone.timedelta(minutes=5):
            perfil.en_linea = True
        else:
            perfil.en_linea = False
        perfil.save()
        context['user_is_online'] = perfil.en_linea
    else:
        context['user_is_online'] = False
    return context

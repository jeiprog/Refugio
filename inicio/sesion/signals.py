from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import Perfil
from django.utils import timezone

@receiver(user_logged_in)
def update_online_status(sender, request, user, **kwargs):
    try:
        perfil = Perfil.objects.get(user=user)
        perfil.en_linea = True
        perfil.ultima_actividad = timezone.now()
        perfil.save()
    except Perfil.DoesNotExist:
        pass

@receiver(user_logged_out)
def update_offline_status(sender, request, user, **kwargs):
    try:
        perfil = Perfil.objects.get(user=user)
        perfil.en_linea = False
        perfil.save()
    except Perfil.DoesNotExist:
        pass

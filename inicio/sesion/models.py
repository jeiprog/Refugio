from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser, User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from PIL import Image 
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, User, Group, Permission
from administra.models import Mascota

class Usuario(AbstractUser):
    nombre_completo = models.CharField(max_length=100)
    foto_de_perfil = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    facebook = models.URLField(max_length=200, null=True, blank=True)
    twitter = models.URLField(max_length=200, null=True, blank=True)
    instagram = models.URLField(max_length=200, null=True, blank=True)

    groups = models.ManyToManyField(
        Group,
        related_name='usuarios_grupo',
        blank=True,
        verbose_name=_('grupos'),
        help_text=_('Los grupos a los que pertenece este usuario. El usuario obtendrá todos los permisos otorgados a cada uno de sus grupos.'),
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='usuarios_permisos',
        blank=True,
        verbose_name=_('permisos de usuario'),
        help_text=_('Permisos específicos para este usuario.'),
    )

    def __str__(self):
        return self.username

class Registrarse(models.Model):
    nombre_completo = models.CharField(max_length=100)
    nombre_usuario = models.CharField(
        max_length=50, 
        unique=True, 
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9]+$',
                message='El nombre de usuario debe contener solo letras y números.'
            )
        ]
    )
    correo = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_usuario

    class Meta:
        db_table = 'registrarse'
        verbose_name = 'Usuario Registrado'
        verbose_name_plural = 'Usuarios Registrados'


class InicioSesion(models.Model):
    usuario = models.ForeignKey(Usuario, related_name='sesiones', on_delete=models.CASCADE)
    contraseña = models.CharField(max_length=50)

    def __str__(self):
        return self.usuario.username

    class Meta:
        db_table = 'inicio_sesion'
        verbose_name = 'Inicio de Sesión'
        verbose_name_plural = 'Inicios de Sesión'


def validate_image_size(value):
    filesize = value.size
    if filesize > 2 * 1024 * 1024:  # 2MB
        raise ValidationError(_('La imagen no puede exceder 2MB.'))


def resize_image(image):
    img = Image.open(image)
    if img.height > 400 or img.width > 400:
        output_size = (400, 400)
        img.thumbnail(output_size)
        img.save(image.path)


from django.utils import timezone

class Perfil(models.Model):
    user = models.OneToOneField(User, related_name='perfil', on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='perfil_fotos/', blank=True, null=True, validators=[validate_image_size])
    facebook = models.URLField(max_length=200, blank=True, null=True)
    twitter = models.URLField(max_length=200, blank=True, null=True)
    instagram = models.URLField(max_length=200, blank=True, null=True)
    en_linea = models.BooleanField(default=False)
    online = models.BooleanField(default=False)
    ultima_actividad = models.DateTimeField(null=True, blank=True, default=timezone.now)

    def save(self, *args, **kwargs):
        # Actualiza el estado en_linea y online basado en la ultima_actividad
        now = timezone.now()
        if self.ultima_actividad and self.ultima_actividad >= now - timezone.timedelta(minutes=5):
            self.en_linea = True
        else:
            self.en_linea = False
        
        self.online = self.en_linea
        super().save(*args, **kwargs)
        if self.foto_perfil:
            resize_image(self.foto_perfil)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def crear_o_actualizar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)
    else:
        instance.perfil.save()


@receiver(post_save, sender=Registrarse)
def crear_usuario_django(sender, instance, created, **kwargs):
    if created:
        User.objects.create_user(username=instance.nombre_usuario, email=instance.correo, password=instance.contraseña)



class Cita(models.Model):
    motivo = models.CharField(max_length=255)
    fecha = models.DateField()
    hora = models.TimeField()
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='citas/', null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    consultada = models.BooleanField(default=False)
    ESTADO_CHOICES = [
        ('Programada', 'Programada'),
        ('No Programada', 'No Programada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='No Programada')
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'cita'
        verbose_name_plural = 'citas'

    def __str__(self):
        return self.motivo

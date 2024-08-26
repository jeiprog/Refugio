from django.contrib import admin
from django.urls import path
from administra import views
from sesion.views import actualizar_estado_cita, admin_dashboard, eliminar_cita, eliminar_mascota, gestionar_perfil, historial_mascotas, login, nuevos_usuarios, registrar,pagina_de_inicio, base, citas, donaciones, admin_citas, crear_mascota, forgotten, RestablecerContraseña, error, redic, si, mis_citas, modificar, crud
from administra.views import excel, mas
from django.conf import settings
from django.conf.urls.static import static
from sesion.views import Usuarios_registrados, cerrar_sesion, loguear

urlpatterns = [
    path('administromiportal/', admin.site.urls),
    path('', pagina_de_inicio, name='pagina_de_inicio'), 
    path('base/', base),
    path('ma/', mas, name='masc'),
    path('citas/', citas, name='citas'),
    path('donaciones/', donaciones, name='donacion'),
    path('cerrar_sesion/', cerrar_sesion, name='cerrar_sesion'),  
    path('forgotten/', forgotten, name='forgotten'),
    path('cambiodecontraseña/<uidb64>/<token>/', RestablecerContraseña.changepassword, name='cambiodecontraseña'),
    path('admin_citas/', admin_citas, name='admin_citas'),
    path('registrar/', Usuarios_registrados.as_view(), name='registrar'),
    path('login/', loguear, name='login'),
    path('error/', error, name='error'),
    path('redic/', redic, name='redirecionar'),
    path('si/', si, name='si'),
    path('gestionar_perfil/', gestionar_perfil, name='gestionar_perfil'),
    path('nuevos_usuarios/', nuevos_usuarios, name='nuevos_usuarios'),
    path('mis_citas/', mis_citas, name='mis_citas'),
    path('crud/', crud, name='crud'),
    path('agregar_mascota/', crear_mascota, name='crear_mascota'),
    path('eliminar/<int:mascota_id>/', eliminar_mascota, name='eliminar'),
    path('historial/', historial_mascotas, name='historial_mascotas'),
    path('modificar/<int:id>/', modificar, name='modificar'),
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('actualizar_estado_cita/<int:cita_id>/', actualizar_estado_cita, name='actualizar_estado_cita'),
    path('excel/', excel, name='excel'),
    path('eliminar_cita/<int:cita_id>/', eliminar_cita, name='eliminar_cita'),
]



urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)

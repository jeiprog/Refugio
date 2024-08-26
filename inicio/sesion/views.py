from datetime import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.paginator import Paginator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.views.generic import View
from django.conf import settings
from .forms import MotivoEliminacionForm, PerfilForm, RegistrarseForm, InicioSesionForm, MascotaForm, CitaForm
from .models import Cita, Perfil, Registrarse, InicioSesion
from administra.models import HistorialMascota, Mascota
from sesion.decorators import login_required_with_message
from django.contrib.auth import logout as auth_logout
from django.utils import timezone

def is_admin(user):
    return user.is_superuser


def registrar(request):
    if request.method == 'POST':
        form = RegistrarseForm(request.POST)
        if form.is_valid():
            nombre_completo = form.cleaned_data['nombre_completo']
            nombre_usuario = form.cleaned_data['nombre_usuario']
            correo = form.cleaned_data['correo']
            contraseña = form.cleaned_data['contraseña']

            usuario = Registrarse(
                nombre_completo=nombre_completo,
                nombre_usuario=nombre_usuario,
                correo=correo,
                contraseña=contraseña
            )
            usuario.save()
            return redirect('login')
    else:
        form = RegistrarseForm()
    return render(request, 'registrarse.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = InicioSesionForm(request.POST)
        if form.is_valid():
            nombre_usuario = form.cleaned_data['usuario']
            contraseña = form.cleaned_data['contraseña']
            usuario_autenticado = authenticate(request, username=nombre_usuario, password=contraseña)
            if usuario_autenticado is not None:
                auth_login(request, usuario_autenticado)
                perfil, created = Perfil.objects.get_or_create(user=usuario_autenticado)
                perfil.en_linea = True
                perfil.ultima_actividad = timezone.now()
                perfil.save()
                return redirect('pagina_de_inicio')
            else:
                messages.error(request, 'Usuario no registrado o contraseña incorrecta')
    else:
        form = InicioSesionForm()
    return render(request, 'index.html', {'form': form})


def usuario_valido(usuario, contraseña):
    try:
        usuario_registrado = Registrarse.objects.get(correo=usuario)
    except Registrarse.DoesNotExist:
        return False  

    return usuario_registrado.contraseña == contraseña


def base(request):
    return render(request, 'base.html')


@user_passes_test(is_admin)
def admin_citas(request):
    estado_seleccionado = request.GET.get('estado', '')

    if estado_seleccionado:
        agendadas = Cita.objects.filter(estado=estado_seleccionado)
    else:
        agendadas = Cita.objects.all()

    return render(request, 'admin_citas.html', {'agendadas': agendadas, 'estado_seleccionado': estado_seleccionado})

def eliminar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)

    cita.delete()
    
    return redirect('admin_citas')


""" =================CRUD========================"""

@user_passes_test(is_admin)
def crud(request):
    masc = Mascota.objects.all()
    return render(request, 'crud.html', {'mascotas': masc})


@user_passes_test(is_admin)
def crear_mascota(request):
    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "")
        return redirect('pagina_de_inicio')  
    else:
        form = MascotaForm()
    return render(request, 'agregar_mascota.html', {'form': form})

@user_passes_test(is_admin)
def eliminar_mascota(request, mascota_id):
    mascota = get_object_or_404(Mascota, id=mascota_id)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo')
        mascota.eliminar_con_historial(motivo)
        return redirect('historial_mascotas')  
    
    return render(request, 'eliminar_mascota.html', {'mascota': mascota})

@user_passes_test(is_admin)
def modificar(request, id):
    mascota = Mascota.objects.get(id=id)
    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES, instance=mascota)
        if form.is_valid():
            messages.success(request, "")
            form.save()
            return redirect('crud')
    else:
        form = MascotaForm(instance=mascota)
    
    return render(request, 'modificar.html', {'form': form, 'mascota': mascota})


""" =================CRUD========================"""


class Usuarios_registrados(View):
    def get(self, request):
        form = RegistrarseForm()
        return render(request, 'registrarse.html', {'form': form})

    def post(self, request):
        form = RegistrarseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pagina_de_inicio')
        return render(request, 'registrarse.html', {'form': form})


def cerrar_sesion(request):
    if request.user.is_authenticated:
        perfil = Perfil.objects.get(user=request.user)
        perfil.online = False
        perfil.save()
    auth_logout(request)
    return redirect('pagina_de_inicio')  

    
def gestionar_perfil(request):
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=request.user.perfil)
        if form.is_valid():
            form.save()
            return redirect('pagina_de_inicio')
    else:
        form = PerfilForm(instance=request.user.perfil)
    return render(request, 'gestionar_perfil.html', {'form': form})


def loguear(request):
    if request.method == 'POST':
        form = InicioSesionForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data.get('usuario')
            contraseña = form.cleaned_data.get('contraseña')
            usuario = User.objects.filter(email=correo).first()
            if usuario is not None:
                usuario = authenticate(request, username=usuario.username, password=contraseña)
                if usuario is not None:
                    try:
                        usuario.perfil
                    except Perfil.DoesNotExist:
                        Perfil.objects.create(user=usuario)
                    auth_login(request, usuario)
                    return redirect('pagina_de_inicio')
            messages.error(request, 'Usuario no registrado o contraseña incorrecta')
    else:
        form = InicioSesionForm()
    return render(request, 'index.html', {'form': form})


def forgotten(request):
    return RestablecerContraseña.forgot(request)


class RestablecerContraseña:
    @staticmethod
    def forgot(request):
        if request.method == 'POST':
            emailUser = request.POST.get('correo_destino')
            user = User.objects.filter(email=emailUser).first()
            if user:
                uidb64 = urlsafe_base64_encode(str(user.id).encode())
                token = default_token_generator.make_token(user)

                reset_link = f"http://localhost:8000/cambiodecontraseña/{uidb64}/{token}/"

                affair = 'Restablecer contraseña'
                html_content = render_to_string('correo.html', {'reset_link': reset_link})
                text_content = strip_tags(html_content)

                email = EmailMultiAlternatives(affair, text_content, 'jeiprogrammers@gmail.com', [emailUser])
                email.attach_alternative(html_content, "text/html")
                email.send()

                return render(request, 'redireccionar.html')
            else:
                return render(request, 'error.html')
        else:
            return render(request, 'forgot.html')

    @staticmethod
    def changepassword(request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            if request.method == 'POST':
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')
                if new_password == confirm_password:
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)
                    return redirect('si') 
                else:
                    return render(request, 'restablecer_contraseña.html', {'error': 'Las contraseñas no coinciden'})
            else:
                return render(request, 'restablecer_contraseña.html')
        else:
            return render(request, 'no.html')


def error(request):
    return render(request, 'error.html')


def redic(request):
    return render(request, 'redirecionar.html')


def si(request):
    return render(request, 'si.html')


@login_required_with_message
def citas(request):
    mascotas = Mascota.objects.all()
    
    if request.method == 'POST':
        form = CitaForm(request.POST, request.FILES)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.usuario = request.user
            cita.save()
            return redirect('mis_citas')
    else:
        form = CitaForm()
    
    return render(request, 'citas.html', {
        'form': form,
        'mascotas': mascotas
    })

@login_required_with_message
def masc(request):
    mascotas = Mascota.objects.all()
    return render(request, 'mascotas_registradas.html', {'mascotas': mascotas})


@login_required_with_message
def donaciones(request):
    return render(request, 'donaciones.html')


def pagina_de_inicio(request):
    masc = Mascota.objects.all()
    paginator = Paginator(masc, 5)
    pagina = request.GET.get("page") or 1
    lista = paginator.get_page(pagina)
    pagina_actual = int(pagina)
    paginas = range(1, lista.paginator.num_pages + 1)

    if request.user.is_superuser:
        num_users = User.objects.exclude(is_superuser=True).count()  
        num_superusers = User.objects.filter(is_superuser=True).count()  
        num_mascotas = Mascota.objects.count()
        num_citas = Cita.objects.count()
        context = {
            'mascota': lista,
            'paginas': paginas,
            'pagina_actual': pagina_actual,
            'num_users': num_users,
            'num_superusers': num_superusers,
            'num_mascotas': num_mascotas,
            'num_citas': num_citas,
        }
        return render(request, 'admin_dashboard.html', context)
    else:
        context = {
            'mascota': lista,
            'paginas': paginas,
            'pagina_actual': pagina_actual
        }
        return render(request, 'vista_general.html', context)

@user_passes_test(is_admin)
def nuevos_usuarios(request):
    admin_users = User.objects.filter(is_superuser=True)
    normal_users = User.objects.filter(is_superuser=False)

    now = timezone.now()
    status_threshold = now - timezone.timedelta(minutes=5)

    admin_profiles = Perfil.objects.filter(user__in=admin_users)
    for perfil in admin_profiles:
        perfil.en_linea = perfil.ultima_actividad and perfil.ultima_actividad > status_threshold
        perfil.online = perfil.en_linea
        perfil.save()

    normal_profiles = Perfil.objects.filter(user__in=normal_users)
    for perfil in normal_profiles:
        perfil.en_linea = perfil.ultima_actividad and perfil.ultima_actividad > status_threshold
        perfil.online = perfil.en_linea
        perfil.save()


    return render(request, 'nuevos_usuarios.html', {'admin_profiles': admin_profiles, 'normal_profiles': normal_profiles})

@login_required_with_message
def mis_citas(request):
    citas = Cita.objects.filter(usuario=request.user)
    return render(request, 'mis_citas.html', {'citas': citas})


@user_passes_test(is_admin)
def admin_dashboard(request):
    if request.user.is_superuser:
        num_users = User.objects.exclude(is_superuser=True).count()  
        num_superusers = User.objects.filter(is_superuser=True).count()  
        num_mascotas = Mascota.objects.count()
        num_citas = Cita.objects.count()

        context = {
            'num_users': num_users,
            'num_superusers': num_superusers,
            'num_mascotas': num_mascotas,
            'num_citas': num_citas,
        }
        return render(request, 'admin_dashboard.html', context)
    else:
        return render(request, 'home.html')

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(is_admin)
def actualizar_estado_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    if request.method == 'POST':
        estado = request.POST.get('estado')
        if cita.estado != estado:
            cita.estado = estado
            cita.save()

            if estado == 'Programada':
                html_content = render_to_string('email/cita_programada.html', {'cita': cita})
                text_content = strip_tags(html_content)

                try:
                    email = EmailMultiAlternatives(
                        subject='Cita Aceptada',
                        body=text_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[cita.usuario.email]
                    )
                    email.attach_alternative(html_content, "text/html")
                    email.send(fail_silently=False)
                    print(f"Email sent to {cita.usuario.email}")
                except Exception as e:
                    print(f"Error al enviar el correo: {e}")

        return redirect('admin_citas')

    return render(request, 'admin_citas.html', {'cita': cita})

def historial_mascotas(request):
    historial = HistorialMascota.objects.all().order_by('-fecha_eliminacion')
    print(f"Historial encontrado: {historial}")
    return render(request, 'historial_mascotas.html', {'historial': historial})

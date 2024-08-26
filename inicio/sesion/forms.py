from django import forms
from administra.models import Mascota
from .models import Cita, Perfil, Registrarse
import re
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class RegistrarseForm(forms.ModelForm):
    nombre_completo = forms.CharField(max_length=100)
    nombre_usuario = forms.CharField(max_length=50)
    correo = forms.EmailField()
    contraseña = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Registrarse
        fields = ['nombre_completo', 'nombre_usuario', 'correo', 'contraseña']

    def clean_nombre_usuario(self):
        nombre_usuario = self.cleaned_data.get('nombre_usuario')
        if not re.match('^[a-zA-Z0-9]+$', nombre_usuario):
            raise forms.ValidationError('El nombre de usuario debe contener solo letras y números.')
        if Registrarse.objects.filter(nombre_usuario=nombre_usuario).exists():
            raise forms.ValidationError('El nombre de usuario ya está en uso.')
        return nombre_usuario

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if Registrarse.objects.filter(correo=correo).exists():
            raise forms.ValidationError('El correo ya está registrado.')
        return correo

    def clean_contraseña(self):
        contraseña = self.cleaned_data.get('contraseña')
        if len(contraseña) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')
        return contraseña

class InicioSesionForm(forms.Form):
    usuario = forms.CharField(max_length=50)
    contraseña = forms.CharField(widget=forms.PasswordInput)
    

class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['nombre', 'foto', 'edad', 'genero', 'raza', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'mascota-form'}),
            'foto': forms.FileInput(attrs={'class': 'mascota-form'}),
            'edad': forms.TextInput(attrs={'class': 'mascota-form'}),
            'genero': forms.TextInput(attrs={'class': 'mascota-form'}),
            'raza': forms.TextInput(attrs={'class': 'mascota-form'}),
            'descripcion': forms.Textarea(attrs={'class': 'mascota-form', 'rows': 3}),
        }

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['motivo', 'fecha', 'hora', 'descripcion', 'mascota', 'imagen']
    
    mascota = forms.ModelChoiceField(
        queryset=Mascota.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['telefono', 'foto_perfil', 'facebook', 'twitter', 'instagram']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Guardar', css_class='btn btn-primary'))


class MotivoEliminacionForm(forms.Form):
    motivo = forms.CharField(widget=forms.Textarea, label='Motivo de Eliminación')
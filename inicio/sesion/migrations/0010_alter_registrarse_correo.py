# Generated by Django 5.0.2 on 2024-06-14 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sesion', '0009_alter_iniciosesion_usuario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registrarse',
            name='correo',
            field=models.EmailField(max_length=60, unique=True),
        ),
    ]
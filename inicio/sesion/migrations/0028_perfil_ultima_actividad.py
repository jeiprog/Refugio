# Generated by Django 5.0.2 on 2024-08-19 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sesion', '0027_remove_perfil_last_activity_perfil_online'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='ultima_actividad',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

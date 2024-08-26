# Generated by Django 5.0.2 on 2024-07-12 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sesion', '0017_cita_agendada'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cita',
            old_name='agendada',
            new_name='consultada',
        ),
        migrations.AddField(
            model_name='cita',
            name='estado',
            field=models.CharField(choices=[('Programada', 'Programada'), ('No Programada', 'No Programada')], default='No Programada', max_length=20),
        ),
    ]
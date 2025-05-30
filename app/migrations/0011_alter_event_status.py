# Generated by Django 5.2 on 2025-05-28 22:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_event_available_tickets'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='status',
            field=models.CharField(choices=[('activo', 'Activo'), ('cancelado', 'Cancelado'), ('reprogramado', 'Reprogramado'), ('agotado', 'Agotado'), ('finalizado', 'Finalizado')], default='activo', max_length=15),
        ),
    ]

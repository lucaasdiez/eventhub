# Generated by Django 5.2 on 2025-05-28 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_merge_20250528_1803'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='available_tickets',
            field=models.PositiveIntegerField(default=0),
        ),
    ]

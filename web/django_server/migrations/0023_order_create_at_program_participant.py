# Generated by Django 2.2.13 on 2020-08-22 17:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_server', '0022_ordering_program'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='programparticipant',
            options={'ordering': ['created_at']},
        ),
    ]

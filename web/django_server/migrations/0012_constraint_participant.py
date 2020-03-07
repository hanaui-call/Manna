# Generated by Django 2.2.10 on 2020-03-07 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_server', '0011_rename_related_name'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='meetingparticipant',
            constraint=models.UniqueConstraint(fields=('meeting', 'participant'), name='meeting_participant_constraint'),
        ),
        migrations.AddConstraint(
            model_name='programparticipant',
            constraint=models.UniqueConstraint(fields=('program', 'participant'), name='program_participant_constraint'),
        ),
    ]
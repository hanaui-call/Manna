# Generated by Django 2.2.10 on 2020-04-08 19:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_server', '0012_constraint_participant'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='space',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='django_server.Space'),
        ),
    ]
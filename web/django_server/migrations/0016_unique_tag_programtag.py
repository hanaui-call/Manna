# Generated by Django 2.2.10 on 2020-04-26 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_server', '0015_programtag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programtag',
            name='tag',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
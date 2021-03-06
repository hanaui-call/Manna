# Generated by Django 2.2.13 on 2020-07-08 21:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_server', '0017_add_tag_program'),
    ]

    operations = [
        migrations.CreateModel(
            name='Zoom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=128, unique=True)),
                ('account_id', models.CharField(max_length=64, unique=True)),
                ('account_pw', models.CharField(max_length=64)),
                ('meeting_room_id', models.CharField(max_length=20, unique=True)),
                ('meeting_room_pw', models.CharField(max_length=20)),
                ('url', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_server.Building')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

# Generated by Django 2.2.10 on 2020-04-26 23:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_server', '0016_unique_tag_programtag'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='program',
            name='close_time',
        ),
        migrations.RemoveField(
            model_name='program',
            name='is_after_school',
        ),
        migrations.RemoveField(
            model_name='program',
            name='open_time',
        ),
        migrations.AddField(
            model_name='program',
            name='tag',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='django_server.ProgramTag'),
        ),
        migrations.AlterField(
            model_name='programtag',
            name='tag',
            field=models.CharField(default='ETC', max_length=100, unique=True),
        ),
    ]

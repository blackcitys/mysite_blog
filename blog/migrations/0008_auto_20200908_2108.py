# Generated by Django 3.0.8 on 2020-09-08 21:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_auto_20200908_2021'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blog',
            name='readed_num',
        ),
        migrations.DeleteModel(
            name='ReadNum',
        ),
    ]

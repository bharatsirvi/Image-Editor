# Generated by Django 4.2.3 on 2023-08-07 18:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('imgeditor', '0009_imagefile_crop_img'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imagefile',
            name='crop_img',
        ),
    ]

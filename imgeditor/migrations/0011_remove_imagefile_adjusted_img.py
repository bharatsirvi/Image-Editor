# Generated by Django 4.2.3 on 2023-08-07 20:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('imgeditor', '0010_remove_imagefile_crop_img'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imagefile',
            name='adjusted_img',
        ),
    ]

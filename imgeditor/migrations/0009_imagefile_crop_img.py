# Generated by Django 4.2.3 on 2023-08-07 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imgeditor', '0008_imagefile_adjusted_img'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagefile',
            name='crop_img',
            field=models.ImageField(blank=True, null=True, upload_to='cropped/'),
        ),
    ]

# Generated by Django 4.2.3 on 2023-08-06 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imgeditor', '0007_imagefile_filtered_img'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagefile',
            name='adjusted_img',
            field=models.ImageField(blank=True, null=True, upload_to='adjusted/'),
        ),
    ]
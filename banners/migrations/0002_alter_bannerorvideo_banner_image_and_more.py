# Generated by Django 4.2.18 on 2025-02-08 09:34

from django.db import migrations, models
from utils.helpers import AzureMediaStorage


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bannerorvideo',
            name='banner_image',
            field=models.ImageField(blank=True, null=True, storage=AzureMediaStorage(), upload_to='banners/'),
        ),
        migrations.AlterField(
            model_name='bannerorvideo',
            name='file_uri',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='bannerorvideo',
            name='video_file',
            field=models.FileField(blank=True, null=True, storage=AzureMediaStorage(), upload_to='videos/'),
        ),
    ]

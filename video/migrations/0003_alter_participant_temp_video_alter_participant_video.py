# Generated by Django 4.2.18 on 2025-02-10 11:19

from utils.helpers import AzureMediaStorage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0002_alter_participant_file_uri_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='temp_video',
            field=models.FileField(blank=True, null=True, upload_to='competition_participants_videos/'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='video',
            field=models.FileField(blank=True, null=True, storage=AzureMediaStorage(), upload_to='competition_participants_videos/'),
        ),
    ]

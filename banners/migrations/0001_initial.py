# Generated by Django 5.1.3 on 2024-11-15 08:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dashboard', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='BannerOrVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('media_type', models.CharField(choices=[('banner', 'Banner'), ('video', 'Video')], default='banner', max_length=10)),
                ('banner_image', models.ImageField(blank=True, null=True, upload_to='banners/')),
                ('video_file', models.FileField(blank=True, null=True, upload_to='videos/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.category')),
            ],
        ),
    ]

# Generated by Django 5.1.2 on 2024-11-11 10:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_register_options'),
        ('dashboard', '0003_alter_competition_options_remove_category_created_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participant',
            name='email',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='name',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='phone_number',
        ),
        migrations.AddField(
            model_name='participant',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounts.register'),
            preserve_default=False,
        ),
    ]
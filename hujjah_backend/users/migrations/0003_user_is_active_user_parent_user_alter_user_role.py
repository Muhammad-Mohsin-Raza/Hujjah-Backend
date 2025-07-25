# Generated by Django 5.2.1 on 2025-06-17 20:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='parent_user',
            field=models.ForeignKey(blank=True, help_text='If this user is an assistant, link them to their lawyer.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assistants', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('user', 'User'), ('admin', 'Admin'), ('assistant', 'Assistant')], default='user', max_length=10),
        ),
    ]

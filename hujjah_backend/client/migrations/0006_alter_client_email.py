# Generated by Django 5.2.1 on 2025-06-14 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0005_client_region_alter_client_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]

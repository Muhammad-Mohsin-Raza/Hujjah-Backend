# Generated by Django 5.2.1 on 2025-06-14 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0004_rename_amount_due_client_amount_paid_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='region',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]

# Generated by Django 5.1.7 on 2025-04-01 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roles', '0004_role_delete_roles_role_roles_is_acti_723ee4_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]

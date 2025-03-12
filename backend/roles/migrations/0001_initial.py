# Generated by Django 5.1.6 on 2025-03-12 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('permissions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Roles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.JSONField(blank=True, default=dict)),
                ('updated_by', models.JSONField(blank=True, default=dict)),
                ('delete_by', models.JSONField(blank=True, default=dict)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('permissions', models.ManyToManyField(blank=True, to='permissions.permissions')),
            ],
            options={
                'db_table': 'Roles',
            },
        ),
    ]

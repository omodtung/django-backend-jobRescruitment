# Generated by Django 5.1.7 on 2025-04-05 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Companies',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('logo', models.CharField(blank=True, max_length=255, null=True)),
                ('isDeleted', models.BooleanField(default=False)),
                ('deletedAt', models.DateTimeField(blank=True, null=True)),
                ('createdBy', models.JSONField(blank=True, null=True)),
                ('updated_by', models.JSONField(blank=True, null=True)),
                ('delete_by', models.JSONField(blank=True, null=True)),
            ],
            options={
                'db_table': 'companies',
            },
        ),
    ]

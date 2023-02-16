# Generated by Django 4.1 on 2023-02-16 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phone', '0013_post'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormStep1',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='FormStep2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('address', models.CharField(blank=True, max_length=200)),
            ],
        ),
    ]
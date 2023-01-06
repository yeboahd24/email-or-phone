# Generated by Django 4.1.4 on 2023-01-06 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phone', '0002_stroke'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('ingredients', models.TextField()),
                ('instructions', models.TextField()),
                ('servings', models.PositiveIntegerField()),
                ('prep_time', models.DurationField()),
                ('cook_time', models.DurationField()),
                ('total_time', models.DurationField()),
                ('difficulty', models.PositiveSmallIntegerField()),
            ],
        ),
    ]

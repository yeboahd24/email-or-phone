# Generated by Django 4.1 on 2023-03-17 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phone', '0017_booktranslation_author_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images/')),
            ],
        ),
    ]
# Generated by Django 4.1.4 on 2023-01-16 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phone', '0005_subscription_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailphoneuser',
            name='otp',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
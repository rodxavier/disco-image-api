# Generated by Django 3.2.13 on 2022-06-22 03:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20220622_0347'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='can_generate_expiring_links',
            field=models.BooleanField(default=False),
        ),
    ]
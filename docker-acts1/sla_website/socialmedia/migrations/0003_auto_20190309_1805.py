# Generated by Django 2.1.5 on 2019-03-09 18:05

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('socialmedia', '0002_auto_20190309_2258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 9, 18, 5, 24, 110816, tzinfo=utc), null=True),
        ),
    ]
# Generated by Django 2.2a1 on 2019-04-18 13:33

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('socialmedia', '0006_auto_20190323_0703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2019, 4, 18, 13, 33, 13, 828221, tzinfo=utc), null=True),
        ),
    ]

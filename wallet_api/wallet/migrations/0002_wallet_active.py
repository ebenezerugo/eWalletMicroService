# Generated by Django 2.0.7 on 2018-07-19 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallet',
            name='active',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]

# Generated by Django 2.1.1 on 2018-09-19 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lims', '0011_auto_20180918_2211'),
    ]

    operations = [
        migrations.AddField(
            model_name='specimenmodel',
            name='volume',
            field=models.FloatField(default=10.0),
            preserve_default=False,
        ),
    ]
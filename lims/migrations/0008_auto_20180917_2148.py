# Generated by Django 2.1.1 on 2018-09-17 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lims', '0007_auto_20180917_2116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specimentype',
            name='type',
            field=models.CharField(max_length=50),
        ),
    ]
# Generated by Django 5.1.3 on 2024-11-23 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_job_weight'),
    ]

    operations = [
        migrations.AlterField(
            model_name='completiontime',
            name='CT',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='job',
            name='weight',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='startingtime',
            name='ST',
            field=models.IntegerField(),
        ),
    ]
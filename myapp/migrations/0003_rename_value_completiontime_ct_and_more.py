# Generated by Django 5.1.3 on 2024-11-21 23:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_completiontime_startingtime'),
    ]

    operations = [
        migrations.RenameField(
            model_name='completiontime',
            old_name='value',
            new_name='CT',
        ),
        migrations.RenameField(
            model_name='startingtime',
            old_name='value',
            new_name='ST',
        ),
    ]

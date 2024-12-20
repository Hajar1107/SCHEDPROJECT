# Generated by Django 5.1.3 on 2024-11-23 21:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_alter_completiontime_ct_alter_job_weight_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='completiontime',
            name='problem',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='myapp.problem'),
        ),
        migrations.AddField(
            model_name='processingtime',
            name='problem',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='myapp.problem'),
        ),
        migrations.AddField(
            model_name='startingtime',
            name='problem',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='myapp.problem'),
        ),
        migrations.CreateModel(
            name='PerformanceMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('T', models.IntegerField()),
                ('E', models.IntegerField()),
                ('FT', models.IntegerField()),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.job')),
                ('problem', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='myapp.problem')),
            ],
        ),
        migrations.CreateModel(
            name='ProblemPerformanceMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Makespan', models.IntegerField()),
                ('TFT', models.IntegerField()),
                ('TT', models.IntegerField()),
                ('TE', models.IntegerField()),
                ('problem', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='myapp.problem')),
            ],
        ),
    ]

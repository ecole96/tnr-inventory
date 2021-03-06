# Generated by Django 3.1.1 on 2021-05-26 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_jobpart_singleuse'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='notes',
            field=models.CharField(blank=True, help_text='Enter any repair notes here (max 2500 characters).', max_length=2500),
        ),
        migrations.AlterField(
            model_name='jobpart_singleuse',
            name='name',
            field=models.CharField(help_text='250 characters max.', max_length=250, verbose_name='Part'),
        ),
    ]

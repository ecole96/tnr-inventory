# Generated by Django 3.1.1 on 2021-01-06 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobpart',
            name='tax',
            field=models.BooleanField(blank=True, default=True, help_text='Checking this adds tax.', verbose_name='Tax?'),
        ),
        migrations.AddField(
            model_name='service',
            name='tax',
            field=models.BooleanField(blank=True, default=False, help_text='Checking this adds tax.', verbose_name='Tax?'),
        ),
    ]
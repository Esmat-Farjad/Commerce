# Generated by Django 5.2 on 2025-04-27 20:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0015_expense_otherincome'),
    ]

    operations = [
        migrations.RenameField(
            model_name='expense',
            old_name='date',
            new_name='date_created',
        ),
        migrations.RenameField(
            model_name='otherincome',
            old_name='date',
            new_name='date_created',
        ),
    ]

# Generated by Django 5.2 on 2025-04-28 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_rename_date_expense_date_created_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expense',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='otherincome',
            name='date_created',
        ),
        migrations.AddField(
            model_name='expense',
            name='created_at',
            field=models.DateField(auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='otherincome',
            name='created_at',
            field=models.DateField(auto_now_add=True),
            preserve_default=False,
        ),
    ]

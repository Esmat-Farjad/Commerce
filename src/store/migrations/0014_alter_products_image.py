# Generated by Django 5.1.7 on 2025-04-23 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_salesdetails_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='image',
            field=models.ImageField(default='default.png', upload_to='item_images'),
        ),
    ]

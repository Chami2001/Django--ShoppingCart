# Generated by Django 4.2.6 on 2024-01-08 13:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Order_Product',
            new_name='Order_Item',
        ),
    ]

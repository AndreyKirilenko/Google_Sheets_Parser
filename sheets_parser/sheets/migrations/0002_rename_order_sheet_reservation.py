# Generated by Django 3.2.9 on 2022-06-15 10:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sheets', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sheet',
            old_name='order',
            new_name='reservation',
        ),
    ]
# Generated by Django 5.1.4 on 2025-01-24 04:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rec_finder', '0003_rename_venue_event_venue_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='venue_id',
            new_name='venue',
        ),
    ]

# Generated by Django 4.2 on 2023-04-22 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0010_alter_attendees_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='heldevent',
            name='number_of_attendees',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
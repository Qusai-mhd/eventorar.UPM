# Generated by Django 4.1.7 on 2023-04-13 03:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EndUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=1)),
            ],
            options={
                'permissions': (('can_register_in_all_published_events', 'To register in all events'), ('can_register_in_male_published_events', 'To register in male events'), ('can_register_in_female_published_events', 'To register in female events')),
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('organizer', models.CharField(choices=[('SE', 'SE CLUB'), ('FC', 'FC CLUB'), ('CARCH', 'C ARCH CLUB'), ('CE', 'CIVIL ENGINEERING CLUB'), ('MEDIA', 'MEDIA CLUB'), ('AI', 'AI CLUB'), ('OTHERS', 'OTHERS')], default='OTHERS', max_length=50)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('semester', models.CharField(max_length=255)),
                ('is_published', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PublishedEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_publication', models.DateField(auto_now_add=True)),
                ('event_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='event.event')),
                ('target_audience', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.group')),
            ],
            options={
                'ordering': ['date_of_publication'],
            },
        ),
        migrations.CreateModel(
            name='RegisteredEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event.publishedevent')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HeldEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_of_attendees', models.PositiveIntegerField()),
                ('average_rating', models.DecimalField(decimal_places=1, default=0, max_digits=1)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event.enduser')),
            ],
        ),
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('certificate', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Attendees',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event.heldevent')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

# Generated by Django 5.2 on 2025-04-13 18:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Elderly', '0005_caregiver_contact_number_alter_doctor_specialization'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='elderlyuser',
            name='date_of_birth',
        ),
        migrations.AlterField(
            model_name='healthrecord',
            name='elderly_user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Elderly.elderlyuser'),
        ),
    ]

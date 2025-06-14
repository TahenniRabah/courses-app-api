# Generated by Django 5.2.1 on 2025-06-04 14:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_enrollment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='enrollment',
            old_name='student',
            new_name='user',
        ),
        migrations.AlterUniqueTogether(
            name='enrollment',
            unique_together={('user', 'course')},
        ),
    ]

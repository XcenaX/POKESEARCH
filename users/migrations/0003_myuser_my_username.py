# Generated by Django 4.2.1 on 2023-11-29 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_verificationphone'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='my_username',
            field=models.TextField(blank=True, null=True),
        ),
    ]

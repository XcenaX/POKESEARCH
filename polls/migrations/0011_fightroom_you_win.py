# Generated by Django 4.2.1 on 2023-10-05 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0010_fightroom_game_ended'),
    ]

    operations = [
        migrations.AddField(
            model_name='fightroom',
            name='you_win',
            field=models.BooleanField(default=False),
        ),
    ]

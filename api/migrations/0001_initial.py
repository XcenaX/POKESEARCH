# Generated by Django 4.2.1 on 2023-10-18 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PokedexPokemon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(default='')),
                ('attack', models.IntegerField(default=0)),
                ('hp', models.IntegerField(default=0)),
                ('defence', models.IntegerField(default=0)),
                ('img', models.TextField(default='')),
                ('weight', models.TextField(default=0)),
                ('height', models.TextField(default=0)),
                ('speed', models.TextField(default=0)),
            ],
        ),
    ]

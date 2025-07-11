# Generated by Django 5.1.6 on 2025-02-28 09:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Coords',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('height', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='DifficultyLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=2, unique=True)),
                ('description', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='PerevalStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='PerevalUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('family_name', models.CharField(max_length=255)),
                ('first_name', models.CharField(max_length=255)),
                ('father_name', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Пользователь перевалов',
                'verbose_name_plural': 'Пользователи перевалов',
            },
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ApiSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('require_authentication', models.BooleanField(default=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Кто изменил')),
            ],
        ),
        migrations.CreateModel(
            name='ModeratorGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='added_moderators', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='moderator_group', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PerevalAdded',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('beautyTitle', models.CharField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('other_titles', models.CharField(blank=True, max_length=255, null=True)),
                ('connect', models.BooleanField(default=False)),
                ('add_time', models.DateTimeField(auto_now_add=True)),
                ('route_description', models.CharField(blank=True, max_length=255, null=True)),
                ('coord', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.coords')),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='main.perevalstatus')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='main.perevaluser')),
            ],
        ),
        migrations.CreateModel(
            name='PerevalImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.CharField(default='', max_length=255)),
                ('title', models.CharField(default='', max_length=255)),
                ('pereval', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='main.perevaladded')),
            ],
        ),
        migrations.CreateModel(
            name='WeatherInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temperature', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('wind_speed', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('precipitation', models.CharField(blank=True, max_length=50, null=True)),
                ('weather_date', models.DateTimeField(auto_now_add=True)),
                ('pereval', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.perevaladded')),
            ],
        ),
        migrations.CreateModel(
            name='PerevalDifficulty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('difficulty', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.difficultylevel')),
                ('pereval', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='difficulties', to='main.perevaladded')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.season')),
            ],
            options={
                'unique_together': {('pereval', 'season')},
            },
        ),
    ]

# Generated by Django 2.2.7 on 2020-03-27 15:12

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('filename', models.CharField(max_length=256)),
                ('size', models.BigIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nickname', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('message_id', models.IntegerField(primary_key=True, serialize=False)),
                ('guild_id', models.IntegerField(default=0)),
                ('content', models.TextField()),
                ('sent', models.DateTimeField()),
                ('state', models.BooleanField(default=True)),
                ('attachments', models.ManyToManyField(to='KgbModule.Attachment')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='KgbModule.Member')),
            ],
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0))),
                ('type', models.SmallIntegerField(default=0)),
                ('content', models.TextField()),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='KgbModule.Message')),
            ],
        ),
    ]

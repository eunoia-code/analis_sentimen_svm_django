# Generated by Django 3.0.7 on 2021-09-18 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sentimen_app', '0002_auto_20210519_1748'),
    ]

    operations = [
        migrations.CreateModel(
            name='TbData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review', models.TextField()),
                ('normalisation', models.TextField()),
                ('label', models.BooleanField()),
            ],
            options={
                'db_table': 'tb_data',
                'managed': False,
            },
        ),
    ]

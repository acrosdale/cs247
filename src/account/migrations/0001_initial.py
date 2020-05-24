# Generated by Django 3.0.5 on 2020-05-24 17:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiverP', models.IntegerField()),
                ('senderP', models.IntegerField()),
                ('published', models.BooleanField(default=False)),
                ('init_time', models.DateTimeField(auto_now_add=True)),
                ('diameter', models.SmallIntegerField()),
                ('delta', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(default=0.0)),
                ('type', models.CharField(choices=[(1, 'bit'), (2, 'ether'), (3, 'zcoin')], max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='Escrow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(default=0.0)),
                ('type', models.CharField(choices=[(1, 'bit'), (2, 'ether'), (3, 'zcoin')], max_length=25)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('paid', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Path',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('src', models.CharField(max_length=25)),
                ('route_len', models.SmallIntegerField(default=1)),
                ('redeemed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Secrets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('secret', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=25)),
                ('currencies', models.ManyToManyField(to='account.Currency')),
            ],
        ),
        migrations.CreateModel(
            name='Transact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('committed', models.BooleanField(default=False)),
                ('contracts', models.ManyToManyField(to='account.Contract')),
            ],
        ),
        migrations.CreateModel(
            name='Hash',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash', models.CharField(max_length=256)),
                ('locked', models.BooleanField(default=True)),
                ('owner', models.CharField(max_length=25)),
                ('paths', models.ManyToManyField(to='account.Path')),
            ],
        ),
        migrations.AddField(
            model_name='contract',
            name='escrow',
            field=models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='account.Escrow'),
        ),
        migrations.AddField(
            model_name='contract',
            name='hashes',
            field=models.ManyToManyField(to='account.Hash'),
        ),
        migrations.AddField(
            model_name='contract',
            name='secrets',
            field=models.ManyToManyField(to='account.Secrets'),
        ),
    ]

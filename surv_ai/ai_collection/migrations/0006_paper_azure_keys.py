# Generated by Django 2.2.2 on 2019-07-03 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_collection', '0005_azurekey'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='azure_keys',
            field=models.ManyToManyField(related_name='papers', to='ai_collection.AzureKey', verbose_name='Azure Keys'),
        ),
    ]

# Generated by Django 2.1.1 on 2018-09-24 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_luigi', '0002_auto_20180920_2015'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TableUpdates',
        ),
        migrations.AlterModelOptions(
            name='taskevent',
            options={'ordering': ['-timestamp']},
        ),
        migrations.RenameField(
            model_name='taskevent',
            old_name='ts',
            new_name='timestamp',
        ),
        migrations.AddField(
            model_name='taskevent',
            name='message',
            field=models.TextField(editable=False, null=True),
        ),
    ]
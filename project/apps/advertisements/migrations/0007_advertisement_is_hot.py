# Generated migration for is_hot field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advertisements', '0006_advertisement_created_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='advertisement',
            name='is_hot',
            field=models.BooleanField(default=False, help_text='Горячее объявление?', verbose_name='Горячее объявление'),
        ),
    ]

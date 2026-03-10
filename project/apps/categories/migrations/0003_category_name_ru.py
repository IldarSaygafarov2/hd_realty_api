# name_ru уже есть в БД — обновляем только state, без SQL

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0002_modeltranslation'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='category',
                    name='name_ru',
                    field=models.CharField(max_length=255, null=True, verbose_name='Название'),
                ),
            ],
            database_operations=[],
        ),
    ]

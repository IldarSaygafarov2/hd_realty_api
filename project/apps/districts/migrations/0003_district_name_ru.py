# name_ru: добавляем только если колонки ещё нет (PostgreSQL)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('districts', '0002_modeltranslation'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='district',
                    name='name_ru',
                    field=models.CharField(max_length=255, null=True, verbose_name='Название'),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql='ALTER TABLE districts_district ADD COLUMN IF NOT EXISTS name_ru VARCHAR(255) NULL;',
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
        ),
    ]

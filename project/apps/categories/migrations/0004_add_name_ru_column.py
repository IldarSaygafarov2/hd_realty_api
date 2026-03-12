# Добавляет колонку name_ru, если её нет (для БД, созданных до исправления 0003)

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0003_category_name_ru'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE categories_category ADD COLUMN IF NOT EXISTS name_ru VARCHAR(255) NULL;',
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

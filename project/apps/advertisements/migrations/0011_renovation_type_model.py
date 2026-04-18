import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advertisements', '0010_listing_card_fields'),
    ]

    operations = [
        # 1. Создать таблицу RenovationType
        migrations.CreateModel(
            name='RenovationType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('slug', models.SlugField(max_length=50, unique=True, verbose_name='Slug')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('name_ru', models.CharField(max_length=100, null=True, verbose_name='Название')),
                ('name_uz', models.CharField(max_length=100, null=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Тип ремонта',
                'verbose_name_plural': 'Типы ремонта',
                'ordering': ['slug'],
            },
        ),
        # 2. Добавить FK поле renovation_type_new (nullable, без конфликта с существующим полем)
        migrations.AddField(
            model_name='advertisement',
            name='renovation_type_new',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='advertisements',
                to='advertisements.renovationtype',
                verbose_name='Тип ремонта',
            ),
        ),
        # 3. Удалить старое CharField поле
        migrations.RemoveField(
            model_name='advertisement',
            name='renovation_type',
        ),
        # 4. Переименовать новое поле
        migrations.RenameField(
            model_name='advertisement',
            old_name='renovation_type_new',
            new_name='renovation_type',
        ),
    ]

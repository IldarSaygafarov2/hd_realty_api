from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("categories", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="name_uz",
            field=models.CharField(max_length=255, null=True, verbose_name="Название"),
        ),
    ]

# Generated by Django 4.1.7 on 2023-10-31 02:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0009_country_favorited_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="normalized_title",
            field=models.CharField(
                blank=True,
                max_length=1000,
                null=True,
                verbose_name="Название статьи в начальной форме",
            ),
        ),
    ]
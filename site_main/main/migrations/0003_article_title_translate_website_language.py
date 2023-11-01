# Generated by Django 4.1.7 on 2023-10-21 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0002_website_sitemap_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="title_translate",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="Перевод названия"
            ),
        ),
        migrations.AddField(
            model_name="website",
            name="language",
            field=models.CharField(
                default="ru", max_length=10, verbose_name="Язык сайта"
            ),
        ),
    ]

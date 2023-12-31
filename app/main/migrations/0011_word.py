# Generated by Django 4.1.7 on 2023-10-31 03:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0010_article_normalized_title"),
    ]

    operations = [
        migrations.CreateModel(
            name="Word",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "text",
                    models.CharField(
                        max_length=100, unique=True, verbose_name="Текст слова"
                    ),
                ),
                (
                    "frequency",
                    models.IntegerField(default=0, verbose_name="Частота слова"),
                ),
                (
                    "articles",
                    models.ManyToManyField(
                        related_name="words", to="main.article", verbose_name="Статьи"
                    ),
                ),
            ],
        ),
    ]

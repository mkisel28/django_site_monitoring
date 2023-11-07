# Generated by Django 4.1.7 on 2023-10-18 11:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Website",
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
                    "name",
                    models.CharField(max_length=255, verbose_name="Название сайта"),
                ),
                ("base_url", models.URLField(verbose_name="Базовый URL")),
                (
                    "last_scraped",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Последний раз обновлено"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Article",
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
                    "title",
                    models.CharField(max_length=255, verbose_name="Название статьи"),
                ),
                ("url", models.URLField(unique=True, verbose_name="Ссылка на статью")),
                ("published_at", models.DateTimeField(verbose_name="Дата публикации")),
                (
                    "website",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="articles",
                        to="main.website",
                        verbose_name="Сайт",
                    ),
                ),
            ],
        ),
    ]
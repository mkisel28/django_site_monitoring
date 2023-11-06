# Generated by Django 4.1.7 on 2023-11-01 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0017_userprofile"),
    ]

    operations = [
        migrations.AlterField(
            model_name="article",
            name="normalized_title",
            field=models.TextField(
                blank=True, null=True, verbose_name="Название статьи в начальной форме"
            ),
        ),
        migrations.AlterField(
            model_name="article",
            name="published_at",
            field=models.DateTimeField(db_index=True, verbose_name="Дата публикации"),
        ),
        migrations.AlterField(
            model_name="article",
            name="title",
            field=models.TextField(verbose_name="Название статьи"),
        ),
        migrations.AlterField(
            model_name="article",
            name="title_translate",
            field=models.TextField(
                blank=True, null=True, verbose_name="Перевод названия"
            ),
        ),
        migrations.AlterField(
            model_name="country",
            name="code",
            field=models.CharField(
                db_index=True, max_length=10, unique=True, verbose_name="Код страны"
            ),
        ),
        migrations.AlterField(
            model_name="ignoredurl",
            name="base_url",
            field=models.URLField(verbose_name="URL для игнорирования статей"),
        ),
        migrations.AlterField(
            model_name="website",
            name="sitemap_url",
            field=models.URLField(
                blank=True, default=None, null=True, verbose_name="Ссылка на SITEMAP"
            ),
        ),
    ]
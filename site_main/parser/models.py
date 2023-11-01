import logging
import time

import pymorphy2
import re

from django.db import models
from django.utils import timezone
from deep_translator import GoogleTranslator
from deep_translator.exceptions import TranslationNotFound
from django.contrib.auth.models import User


logger = logging.getLogger("models")

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    telegram_chat_id = models.CharField(max_length=255, null=True, blank=True)
    telegram_notifications = models.BooleanField(default=False)
    class Meta:
        app_label = 'main'

class IgnoredURL(models.Model):
    base_url = models.URLField(verbose_name="Base URL to Ignore")
    users = models.ManyToManyField(User, related_name="ignored_urls", blank=True)  # добавлено

    def __str__(self):
        return self.base_url

    class Meta:
        app_label = 'main'


class Country(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название страны")
    code = models.CharField(max_length=10, verbose_name="Код страны", unique=True)
    favorited_by = models.ManyToManyField(User, related_name="favorite_countries", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'main'


class Website(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название сайта")
    base_url = models.URLField(verbose_name="Базовый URL")
    sitemap_url = models.URLField(verbose_name="SITEMAP URL", default=None, null=True, blank=True)
    last_scraped = models.DateTimeField(null=True, blank=True, verbose_name="Последний раз обновлено")
    language = models.CharField(max_length=10, verbose_name="Язык сайта", default="ru")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Страна")

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'main'


class Article(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="articles", verbose_name="Сайт")
    title = models.CharField(max_length=1000, verbose_name="Название статьи")
    url = models.URLField(max_length=1000, unique=True, verbose_name="Ссылка на статью")
    published_at = models.DateTimeField(verbose_name="Дата публикации")
    title_translate = models.CharField(max_length=1000, verbose_name="Перевод названия", blank=True, null=True)
    normalized_title = models.CharField(max_length=1000, verbose_name="Название статьи в начальной форме", blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        app_label = 'main'

    @classmethod
    def create(cls, website, title, url, published_at):
        # Проверяем, существует ли статья с таким URL
        if not cls.objects.filter(url=url).exists():
            article = cls(website=website, title=title,
                          url=url, published_at=published_at)

            # Если язык веб-сайта не русский, переводим заголовок
            if website.language not in ["ru", "RU"]:
                article.title_translate = translate_text(from_lang=website.language,
                                                         to_translate=title
                                                         )
            morph = pymorphy2.MorphAnalyzer(lang='ru')

            config = Configuration.objects.first()
            black_list = tuple(
                tag if tag != "NONE" else None for tag in config.black_list_tags.split(','))
            black_list_word = tuple(config.black_list_words.split(','))

            if website.language in ["ru", "RU"]:
                words = article.title
            else:
                words = article.title_translate

            text = re.sub(r'[^\w\s-]', '', words).split()
            normalized_words = [morph.parse(x)[0].normal_form for x in text if len(x) > 1 and morph.parse(x)[
                0].tag.POS not in black_list and x not in black_list_word]

            article.normalized_title = ' '.join(normalized_words)

            website.last_scraped = timezone.now()

            website.save()
            article.save()


            # Проверка и сохранение упоминаний в TrackedWordMention
            tracked_words = TrackedWord.objects.all()
            for word in tracked_words:
                if word.keyword and (
                (article.title and word.keyword.lower() in article.title.lower()) or 
                (article.title_translate and word.keyword.lower() in article.title_translate.lower()) or 
                (article.normalized_title and word.keyword.lower() in article.normalized_title.lower())
                ):
                    mention = TrackedWordMention.objects.create(word=word, article=article)
                    check_and_send_notifications(mention)



            return article


class Word(models.Model):
    text = models.CharField(max_length=100, unique=False, verbose_name="Текст слова")
    frequency = models.IntegerField(default=0, verbose_name="Частота слова")
    articles = models.ManyToManyField(Article, related_name="words", verbose_name="Статьи")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    class Meta:
        app_label = 'main'

    def __str__(self):
        return self.text


class TrackedWord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tracked_words")
    keyword = models.CharField(max_length=255, verbose_name="Отслеживаемое слово")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время добавления")

    class Meta:
        unique_together = ('user', 'keyword')
        app_label = 'main'


class TrackedWordMention(models.Model):
    word = models.ForeignKey(TrackedWord, on_delete=models.CASCADE, related_name="mentions")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="mentions")
    mentioned_at = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        app_label = 'main'
        unique_together = ('word', 'article')

class Configuration(models.Model):
    name = models.CharField(max_length=255, unique=True,
                            verbose_name="Configuration Name")
    black_list_tags = models.TextField(
        default="NPRO,INTJ,CONJ,PREP,PRED,ADJF,NPRO,ADVB,ADJS,PRCL,INFN,VERB",
        verbose_name="Черный список тегов(форм слов) для morph (comma-separated)"
    )
    black_list_words = models.TextField(
        default="ТАСС",
        verbose_name="Черный список слов для morph (comma-separated)"
    )
    hours = models.PositiveIntegerField(
        default=1, verbose_name="Время для анализа статей(ч)")
    top_words_count = models.PositiveIntegerField(
        default=10, verbose_name="Счетчик Top Words")

    class Meta:
        app_label = 'main'


def translate_text(from_lang, to_translate):

    MAX_RETRIES = 10
    for i in range(MAX_RETRIES):
        try:
            translated_text = GoogleTranslator(
                source=from_lang, target='ru').translate(to_translate)
            logger.info(f"Попытка перевода №{i+1}. Успешно.")

            return translated_text
        except TranslationNotFound:
            logger.error(f"Попытка перевода №{i+1}. Ошибка перевода.")
            time.sleep(1)
    raise TranslationNotFound(
        f"Не удалось перевести после {MAX_RETRIES} попыток")



from telegram_bot import send_telegram_notification

def check_and_send_notifications(tracked_word_mention):
    tracked_word = tracked_word_mention.word
    article = tracked_word_mention.article

    user = tracked_word.user

    try:
        user_profile = user.userprofile
        if user_profile.telegram_notifications and user_profile.telegram_chat_id:
            send_telegram_notification(user_profile.telegram_chat_id, article, tracked_word.keyword)
    except Exception as e:
        logger.error(f"Failed to send notification to user {user.username} with error {e}")
        pass
import pymorphy2
import re
from deep_translator import GoogleTranslator

from django.db import models
from django.utils import timezone
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,  db_index=True)
    telegram_chat_id = models.CharField(max_length=255, null=True, blank=True)
    telegram_notifications = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user
    
class IgnoredURL(models.Model):
    base_url = models.URLField(verbose_name="URL для игнорирования статей")
    users = models.ManyToManyField(User, related_name="ignored_urls", blank=True)  # добавлено

    def __str__(self):
        return self.base_url



class Country(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название страны")
    code = models.CharField(max_length=10, verbose_name="Код страны", unique=True, db_index=True)
    favorited_by = models.ManyToManyField(User, related_name="favorite_countries", blank=True)

    def __str__(self):
        return self.name
    

         
class Website(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название сайта")
    base_url = models.URLField(verbose_name="Базовый URL")
    sitemap_url = models.URLField(verbose_name="Ссылка на SITEMAP", default=None, null=True, blank=True)
    last_scraped = models.DateTimeField(null=True, blank=True, verbose_name="Последний раз обновлено")
    language = models.CharField(max_length=10, verbose_name="Язык сайта", default="ru")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Страна")
    favorited_by = models.ManyToManyField(User, related_name="favorite_websites", blank=True) 


    def __str__(self):
        return self.name
    

    
class Article(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="articles", verbose_name="Сайт", db_index=True)
    title = models.TextField(verbose_name="Название статьи")
    url = models.URLField(max_length=1000, unique=True, verbose_name="Ссылка на статью")
    published_at = models.DateTimeField(verbose_name="Дата публикации", db_index=True)
    title_translate = models.TextField(verbose_name="Перевод названия", blank=True, null=True)
    normalized_title = models.TextField(verbose_name="Название статьи в начальной форме", blank=True, null=True)

    def __str__(self):
        return self.title


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
                    #check_and_send_notifications(mention)



            return article

class Word(models.Model):
    text = models.CharField(max_length=100, unique=False, verbose_name="Текст слова")
    frequency = models.IntegerField(default=0, verbose_name="Частота слова")
    articles = models.ManyToManyField(Article, related_name="words", verbose_name="Статьи")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")


    def __str__(self):
        return self.text

class TrackedWord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tracked_words", db_index=True)
    keyword = models.CharField(max_length=255, verbose_name="Отслеживаемое слово")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время добавления")

    class Meta:
        unique_together = ('user', 'keyword')

    def save(self, *args, **kwargs):
        # Сначала сохраняем слово
        super(TrackedWord, self).save(*args, **kwargs)
        
        # Проверяем все статьи на наличие этого слова
        articles_with_word = Article.objects.filter(
            Q(title__icontains=self.keyword) |
            Q(title_translate__icontains=self.keyword) |
            Q(normalized_title__icontains=self.keyword)
        )
        # Создаем записи в TrackedWordMention для каждой статьи, содержащей это слово
        for article in articles_with_word:
            TrackedWordMention.objects.get_or_create(word=self, article=article, mentioned_at= article.published_at)


class TrackedWordMention(models.Model):
    word = models.ForeignKey(TrackedWord, on_delete=models.CASCADE, related_name="mentions")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="mentions")
    mentioned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('word', 'article')

class Configuration(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Configuration Name")
    black_list_tags = models.TextField(
        default="NPRO,INTJ,CONJ,PREP,PRED,ADJF,NPRO,ADVB,ADJS,PRCL,INFN,VERB",
        verbose_name="Черный список тегов(форм слов) для morph (comma-separated)"
    )
    black_list_words = models.TextField(
        default="ТАСС",
        verbose_name="Черный список слов для morph (comma-separated)"
    )
    hours = models.PositiveIntegerField(default=1, verbose_name="Время для анализа статей(ч)")
    top_words_count = models.PositiveIntegerField(default=10, verbose_name="Счетчик Top Words")

    def __str__(self):
        return self.name



def translate_text(from_lang, to_translate):
    translated_text = GoogleTranslator(source=from_lang, target='ru').translate(to_translate)
    return translated_text


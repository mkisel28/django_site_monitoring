import logging

from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User

from utils.service_utils import check_and_send_notifications, translate_text_to_eng, translate_text_to_ru
from utils.text_helpers import get_normalized_words_from_text


logger = logging.getLogger("models")

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,  db_index=True)
    telegram_chat_id = models.CharField(max_length=255, null=True, blank=True)
    telegram_notifications = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'main'

class IgnoredURL(models.Model):
    base_url = models.URLField(verbose_name="URL для игнорирования статей")
    users = models.ManyToManyField(User, related_name="ignored_urls", blank=True)

    def __str__(self):
        return self.base_url

    class Meta:
        app_label = 'main'


class Country(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название страны")
    code = models.CharField(max_length=10, verbose_name="Код страны", unique=True, db_index=True)
    favorited_by = models.ManyToManyField(User, related_name="favorite_countries", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'main'


class Website(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пользователь")

    name = models.CharField(max_length=255, verbose_name="Название сайта")
    base_url = models.URLField(verbose_name="Базовый URL")
    sitemap_url = models.URLField(verbose_name="Ссылка на SITEMAP", default=None, null=True, blank=True)
    last_scraped = models.DateTimeField(null=True, blank=True, verbose_name="Последний раз обновлено")
    language = models.CharField(max_length=10, verbose_name="Язык сайта", default="ru")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Страна")
    favorited_by = models.ManyToManyField(User, related_name="favorite_websites", blank=True) 

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'main'


class Article(models.Model):
    class CategoryChoices(models.TextChoices):
        PARENTS = 'PARENTS', 'Родители'
        WELLNESS = 'WELLNESS', 'Здоровье'
        PARENTING = 'PARENTING', 'Воспитание'
        COMEDY = 'COMEDY', 'Комедия'
        POLITICS = 'POLITICS', 'Политика'
        BLACK_VOICES = 'BLACK VOICES', 'Черные Голоса'
        QUEER_VOICES = 'QUEER VOICES', 'Квир-Голоса'
        ENTERTAINMENT = 'ENTERTAINMENT', 'Развлечения'
        CULTURE_ARTS = 'CULTURE & ARTS', 'Культура и Искусство'
        TECH = 'TECH', 'Технологии'
        RELIGION = 'RELIGION', 'Религия'
        STYLE_BEAUTY = 'STYLE & BEAUTY', 'Стиль и Красота'
        HEALTHY_LIVING = 'HEALTHY LIVING', 'Здоровый Образ Жизни'
        TRAVEL = 'TRAVEL', 'Путешествия'
        GREEN = 'GREEN', 'Экология'
        IMPACT = 'IMPACT', 'Влияние'
        BUSINESS = 'BUSINESS', 'Бизнес'
        DIVORCE = 'DIVORCE', 'Развод'
        SCIENCE = 'SCIENCE', 'Наука'
        SPORTS = 'SPORTS', 'Спорт'
        LATINO_VOICES = 'LATINO VOICES', 'Латиноамериканские Голоса'
        WORLD_NEWS = 'WORLD NEWS', 'Мировые Новости'
        HOME_LIVING = 'HOME & LIVING', 'Дом и Жизнь'
        MEDIA = 'MEDIA', 'Медиа'
        US_NEWS = 'U.S. NEWS', 'Новости США'
        TASTE = 'TASTE', 'Вкус'
        FOOD_DRINK = 'FOOD & DRINK', 'Еда и Напитки'
        WEIRD_NEWS = 'WEIRD NEWS', 'Странные Новости'
        STYLE = 'STYLE', 'Стиль'
        WOMEN = 'WOMEN', 'Женщины'
        ARTS_CULTURE = 'ARTS & CULTURE', 'Искусство и Культура'
        CRIME = 'CRIME', 'Преступность'
        MONEY = 'MONEY', 'Деньги'
        WEDDINGS = 'WEDDINGS', 'Свадьбы'
        ARTS = 'ARTS', 'Искусства'
        WORLDPOST = 'WORLDPOST', 'Мировой Пост'
        THE_WORLDPOST = 'THE WORLDPOST', 'Мировой Пост (THE)'
        EDUCATION = 'EDUCATION', 'Образование'
        COLLEGE = 'COLLEGE', 'Колледж'
        GOOD_NEWS = 'GOOD NEWS', 'Хорошие Новости'
        FIFTY = 'FIFTY', 'Пятьдесят'
        ENVIRONMENT = 'ENVIRONMENT', 'Окружающая Среда'
        
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="articles", verbose_name="Сайт", db_index=True)
    title = models.TextField(verbose_name="Название статьи")
    url = models.URLField(max_length=1000, unique=True, verbose_name="Ссылка на статью")
    published_at = models.DateTimeField(verbose_name="Дата публикации", db_index=True)
    eng_title = models.TextField(verbose_name="Название статьи на английском", blank=True, null=True)
    normalized_title = models.TextField(verbose_name="Название статьи в начальной форме", blank=True, null=True)
    category = models.CharField(max_length=50, choices=CategoryChoices.choices, verbose_name="Категория", blank=True, null=True, db_index=True)

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
                article.title_translate = translate_text_to_ru(from_lang=website.language,
                                                         to_translate=title
                                                         )
            if website.language not in ["en", "EN"]:
                article.eng_title = translate_text_to_eng(from_lang=website.language, 
                                                          to_translate=title
                                                        )
            else:
                article.eng_title = title

            if website.language in ["ru", "RU"]:
                words = article.title
            else:
                words = article.title_translate
            config = Configuration.objects.first()
            normalized_words = get_normalized_words_from_text(words, config)
            article.normalized_title = ' '.join(normalized_words)

            website.last_scraped = timezone.now()

            website.save()
            article.save()


            # Проверка и сохранение упоминаний в TrackedWordMention
            tracked_words = TrackedWord.objects.all()
            users_keywords_dict = {} 
            for word in tracked_words:
                if word.keyword and (
                (article.title and word.keyword.lower() in article.title.lower()) or 
                (article.title_translate and word.keyword.lower() in article.title_translate.lower()) or 
                (article.normalized_title and word.keyword.lower() in article.normalized_title.lower())
                ):
                    mention = TrackedWordMention.objects.create(word=word, article=article)
                    if word.user not in users_keywords_dict:
                        users_keywords_dict[word.user] = []
                    users_keywords_dict[word.user].append(word.keyword)
            for user, keywords in users_keywords_dict.items():
                check_and_send_notifications(user, article, keywords)


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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tracked_words",  db_index=True)
    keyword = models.CharField(max_length=255, verbose_name="Отслеживаемое слово",db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время добавления")

    class Meta:
        unique_together = ('user', 'keyword')
        app_label = 'main'
        
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




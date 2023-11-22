from datetime import timedelta
from collections import Counter
import logging

from models import Website, Article, IgnoredURL, Word, Configuration
from django.db import transaction
from django.db import DatabaseError
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

import concurrent.futures

from parsers.utils import format_date
from parsers import parse

logger = logging.getLogger("database")
logger_tw = logging.getLogger("top_words_logger")


def save_to_db(website_id, data):
    try:
        website = Website.objects.get(pk=website_id)
        ignored_urls = IgnoredURL.objects.values_list('base_url', flat=True)
    except (Website.DoesNotExist):
        logger.exception(f"Error getting website with id {website_id}")
        return
    except DatabaseError:
        logger.exception(f"Database error getting website with id {website_id}")
        return


    for entry in data:
        try:
            title = entry.get("title", None)
            url = entry.get("article_url", None)
            published_at = entry.get("lastmod", None)

            if any(url.startswith(ignored_url) for ignored_url in ignored_urls):
                continue

            if not Article.objects.filter(url=url).exists():
                published_at = format_date(published_at, website_id)
                Article.create(website, title, url, published_at)
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            logger.debug(f"Details: {website}, {title}, {url}, {published_at}")


# def main():
#     while True:
#         websites = Website.objects.all()
#         for website in websites:
#             logger.info(f'Начал парсинг сайта: {website.name}')
#             with transaction.atomic():
#                 sitemap_url = website.sitemap_url
#                 base_url = website.base_url
#                 if sitemap_url:
#                     website_id = website.id
#                     data = parse(base_url, sitemap_url)
#                     if data:
#                         save_to_db(website_id, data)
#                     else: logger.warning(f"Пустой парсинг controller.py __main__: {website}" )
#         logger.info("COMPLATED PARS ALL SITE")
#         time.sleep(60)


# def test(id, base_url, sitemap_url):

#     data = parse(base_url, sitemap_url)
#     if data:
#         save_to_db(id, data)


def worker(website):
    try:
        thread_n = website.id
        logger.info(f'[{thread_n}] Начал парсинг сайта: {website.name}')

        sitemap_url = website.sitemap_url
        base_url = website.base_url
        if sitemap_url:
            website_id = website.id
            data = parse(base_url, sitemap_url)
            if data:
                save_to_db(website_id, data)
            else:
                logger.warning(f"[{thread_n}] Пустой парсинг controller.py: {website}")
    except Exception as e:
        logger.exception(f"[{website.id}] Ошибка при парсинге сайта {website.name}: {e}")


def main():
    try:
        websites = Website.objects.all()
        logger.info("Start ThreadPoolExecutor")

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(worker, websites)

        logger.info("COMPLETED PARSING ALL SITES")
    except Exception as e:
        logger.exception(f"Error in main function: {e}")


#   фильтрует статьи за последний час
def top_words():
    logger_tw.info(f"Начал обработку top_words")
    
    try:
        config = Configuration.objects.first()
        if not config:
            raise ObjectDoesNotExist("Конфигурация не найдена")
        HOURS = config.hours
        TOP_COUNT = config.top_words_count

        one_hour_ago = timezone.now() - timedelta(hours=HOURS)
        recent_articles = Article.objects.filter(published_at__gte=one_hour_ago)

        all_words = [word for article in recent_articles if article.normalized_title
                     for word in article.normalized_title.split()]

        word_counts = Counter(all_words)
        top_10_words = word_counts.most_common(TOP_COUNT)
        
        
    except ObjectDoesNotExist as e:
        logger_tw.warning(f"Не удалось найти необходимый объект: {e}")
        return
    except DatabaseError as e:
        logger_tw.error(f"Ошибка базы данных: {e}")
        return
    except Exception as e:
        logger_tw.exception(f"Непредвиденная ошибка при подготовке данных для top_words: {e}")
        return
    try:
        # Удаление старых тегов (30 дней)
        cutoff_time = timezone.now() - timedelta(days=30)
        Word.articles.through.objects.filter(word__timestamp__lt=cutoff_time).delete()
        Word.objects.filter(timestamp__lt=cutoff_time).delete()
    except DatabaseError as e:
        logger_tw.error(f"Ошибка базы данных при очистке старых слов: {e}")
    except Exception as e:
        logger_tw.exception(f"Непредвиденная ошибка при очистке старых слов: {e}")
        
    try:
        for word_text, count in top_10_words:
            word, created = Word.objects.get_or_create(text=word_text)
            word.frequency = count
            word.save()
            word.articles.add(*[article for article in recent_articles if word_text in (article.normalized_title or "").split()])
    except DatabaseError as e:
        logger_tw.error(f"Ошибка базы данных при сохранении слов: {e}")
    except Exception as e:
        logger_tw.exception(f"Непредвиденная ошибка при сохранении слов: {e}")

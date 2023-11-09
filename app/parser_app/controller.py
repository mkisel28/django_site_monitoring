import logging
from .models import Website, Article, IgnoredURL, Word, Configuration
from django.db import transaction
from parsers.utils import format_date
from parsers import parse
from django.db import DatabaseError

logger = logging.getLogger("database")

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
        title = entry.get("title", None) 
        url = entry.get("article_url", None) 
        published_at = entry.get("lastmod", None) 

        if any(url.startswith(ignored_url) for ignored_url in ignored_urls):
            continue

        if not Article.objects.filter(url=url).exists():
            published_at = format_date(published_at, website_id)
            try:
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

import threading

def worker(website, thread_n):
    logger.info(f'[{thread_n}] Начал парсинг сайта: {website.name}')

    sitemap_url = website.sitemap_url
    base_url = website.base_url
    if sitemap_url:
        website_id = website.id
        data = parse(base_url, sitemap_url)
        if data:
            save_to_db(website_id, data)
        else: 
            logger.warning(f"[{thread_n}] Пустой парсинг controller.py: {website}" )


def main():
    websites = Website.objects.all()
    threads = []
    for website in websites:

        thread_n = website.id
        t = threading.Thread(target=worker, args=(website,thread_n))
        threads.append(t)
        t.start()
        if len(threads) >= 20:  # Если активно 10 потоков, ожидаем их завершения
            for t in threads:
                t.join()
            threads = []  # Очищаем список потоков
    # Ожидаем завершения оставшихся потоков
    for t in threads:
        t.join()
    logger.info("COMPLETED PARSING ALL SITES")






from django.utils import timezone

from datetime import  timedelta
from collections import Counter

# 1. Отфильтруйте статьи за последний час.
def top_words():
    config = Configuration.objects.first() 
    HOURS = config.hours
    TOP_COUNT = config.top_words_count

    one_hour_ago = timezone.now() - timedelta(hours=HOURS)
    recent_articles = Article.objects.filter(published_at__gte=one_hour_ago)

    all_words = []
    for article in recent_articles:
        if article.normalized_title:
            all_words.extend(article.normalized_title.split())

    word_counts = Counter(all_words)
    top_10_words = word_counts.most_common(TOP_COUNT)
    #Удаление старых тегов (30 дней)
    cutoff_time = timezone.now() - timedelta(days=30)
    Word.articles.through.objects.filter(word__timestamp__lt=cutoff_time).delete()
    Word.objects.filter(timestamp__lt=cutoff_time).delete()


    # Сохранение слов и их частот в базе данных
    for word_text, count in top_10_words:
        word = Word(text=word_text, frequency=count)
        word.save() 
        # Привязка слова к статьям, в которых оно встречается
        for article in recent_articles:
            if article.normalized_title:
                if word_text in article.normalized_title.split():
                    word.articles.add(article)

        word.save()
    # word_query = "счёт"
    # word_obj = Word.objects.get(text=word_query)
    # related_articles = word_obj.articles.all()
    # return top_10_words, related_articles


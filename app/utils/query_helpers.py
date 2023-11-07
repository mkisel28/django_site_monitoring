from typing import List
from django.db.models import Q


from .text_helpers import normalize_word
from django.db.models.query import QuerySet

def get_articles_with_word(keyword: str, Article) -> 'QuerySet[Article]':
    """
    Извлекает статьи, содержащие предоставленное ключевое слово.
    
    Args:
    - keyword: Ключевое слово для поиска.

    Returns:
    - QuerySet статей, содержащих ключевое слово.
    """
    return Article.objects.filter(
        Q(title__icontains=keyword) |
        Q(title_translate__icontains=keyword) |
        Q(normalized_title__icontains=keyword)
    )


def build_search_query(search_post: List[str]) -> Q:
    """
    Создает запрос для поиска нескольких слов в статьях. C Учетом нормализованных слов.
    
    Args:
    - search_post: Список слов для поиска.

    Returns:
    - Объект запроса.
    """
    q_objects = Q()
    for word in search_post:
        normalized_word = normalize_word(word)
        q_objects &= (
            Q(title__icontains=word) | 
            Q(title_translate__icontains=word) |
            Q(normalized_title__icontains=word) |
            Q(title__icontains=normalized_word) |
            Q(title_translate__icontains=normalized_word) |
            Q(normalized_title__icontains=normalized_word)
        )
    return q_objects
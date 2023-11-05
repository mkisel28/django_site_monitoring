from typing import List, Dict, Any
import pymorphy2
import re

morph = pymorphy2.MorphAnalyzer(lang='ru')

def create_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Заменяет название статьи на переведенное название, если оно существует, и удаляет title_translate из словаря.
    
    Args:
    - atricles: Список словарей статей.

    Returns:

    - articles: Измененный список статей.
    """
    for article in articles:
        if article['title_translate']:
            article['title'] = article['title_translate']
            del article['title_translate']
    return articles


def normalize_word(word: str) -> str:
    """
    Возвращает нормализованную форму предоставленного слова.
    
    Args:
    - word: Слово для нормализации.

    Returns:
    - Нормализованная форма слова.
    """
    normalized_word = morph.parse(word)[0].normal_form
    return normalized_word


def get_normalized_words_from_text(text: str, config) -> List[str]:
    """
    Удаляет нежелательные символы из текста и возвращает список нормализованных слов.
    
    Args:
    - text: Текст для обработки.
    - black_list_tags: Список нежелательных морфологических тегов.
    - black_list_words: Список нежелательных слов.

    Returns:
    - Список нормализованных слов.
    """
    black_list = tuple(
        tag if tag != "NONE" else None for tag in config.black_list_tags.split(','))
    black_list_word = tuple(config.black_list_words.split(','))  
    text = re.sub(r'[^\w\s-]', '', text).split()
    normalized_words = [
        morph.parse(x)[0].normal_form 
        for x in text if len(x) > 1 
        and morph.parse(x)[0].tag.POS not in black_list
        and x not in black_list_word
    ]
    return normalized_words



import requests
import logging
import time

from deep_translator import GoogleTranslator
from deep_translator.exceptions import TranslationNotFound



logger = logging.getLogger("notification")


def translate_text(from_lang: str, to_translate: str) -> str:
    """
    Переводит текст на русский язык, с повторными попытками в случае ошибок.
    
    Args:
    - from_lang: Исходный язык текста.
    - to_translate: Текст для перевода.

    Returns:
    - Переведенный текст.
    """
    MAX_RETRIES = 10
    for i in range(MAX_RETRIES):
        try:
            translated_text = GoogleTranslator(source=from_lang, target='ru').translate(to_translate)
            logger.info(f"Попытка перевода №{i+1}. Успешно.")
            return translated_text
        except TranslationNotFound:
            logger.error(f"Попытка перевода №{i+1}. Ошибка перевода.")
            time.sleep(1)
    raise TranslationNotFound(f"Не удалось перевести после {MAX_RETRIES} попыток")



def check_and_send_notifications(tracked_word_mention):
    """
    Отправляет уведомление о упоминании отслеживаемого слова пользователю через Telegram.
    
    Args:
    - tracked_word_mention: Объект TrackedWordMention.
    """
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






def send_telegram_notification(chat_id, article, tracked_word):
    """
    Отправляет уведомление о упоминании отслеживаемого слова пользователю через Telegram.

    Args:
    - chat_id: ID чата Telegram.
    - article: Объект Article.
    - tracked_word: Отслеживаемое слово.

    Exceptions:
    - requests.HTTPError: Ошибка отправки уведомления.

    """
    title = article.title_translate if article.title_translate else article.title
    TOKEN= '5839656131:AAEi-43ttcx3nDEh83ij0lz-ajh1EIfp7CU'
    message = f"Новая статья с вашим отслеживаемым словом: {tracked_word} \n\nНазвание: {title}\n\n<{article.url}>"
    try:
        response = requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}")
        response.raise_for_status()
    except requests.HTTPError as e:
        logger.error(f"Error sending telegram notification: {e}")
        logger.debug(f"Details: {chat_id}, {article}, {tracked_word}")
    except Exception as e:
        logger.error(f"Error sending telegram notification: {e}")
        logger.debug(f"Details: {chat_id}, {article}, {tracked_word}")


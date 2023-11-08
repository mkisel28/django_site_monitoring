# from telegram import Bot

# async def send_telegram_notification(chat_id, article):
#     bot = Bot(token='5839656131:AAEi-43ttcx3nDEh83ij0lz-ajh1EIfp7CU')
#     message = f"Новая статья с вашим отслеживаемым словом: {article} ({article})"
#     await bot.send_message(chat_id=chat_id, text=message)


# import asyncio
# def main():
#     while True:
#         asyncio.run(send_telegram_notification(1689568914,"fdfd" ))
import requests

import logging
logger = logging.getLogger("notification")



class TelegramLoggingHandler(logging.Handler):
    def __init__(self, token, chat_id):
        super().__init__()
        self.TOKEN = token
        self.chat_id = chat_id

    def emit(self, record):
        message = self.format(record)
        try:
            requests.get(f"https://api.telegram.org/bot{self.TOKEN}/sendMessage?chat_id={self.chat_id}&text={message}")
        except Exception:
            pass
        
def send_telegram_notification(chat_id, article, tracked_word):
    title = article.title_translate if article.title_translate else article.title
    TOKEN= '5839656131:AAEi-43ttcx3nDEh83ij0lz-ajh1EIfp7CU'
    message = f"Новая статья с вашим отслеживаемым словом: {tracked_word} \n\nНазвание: {title}\n\n<{article.url}>"
    try:
        response = requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}")
        response.raise_for_status()

    except Exception as e:
        logger.error(f"Error sending telegram notification: {e}")
        logger.debug(f"Details: {chat_id}, {article}, {tracked_word}")


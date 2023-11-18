import html
import requests
from datetime import datetime, timedelta
import logging
logger = logging.getLogger("utils")

def clean_html_entities(input_str: str) -> str:
    """Преобразует HTML-сущности в их фактические символы."""
    return html.unescape(input_str)


def get_headers():
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    return headers


from datetime import datetime, timedelta
from email.utils import parsedate_tz, mktime_tz
from zoneinfo import ZoneInfo  

def format_date(published_at_str, website_id):
    formats = [
        '%a, %d %b %Y %H:%M:%S %z',   # 'Mon, 23 Oct 2023 19:07:17 +0300'
        '%d %b %Y %H:%M:%S %z',       # '23 Oct 2023 18:52:33 +0330'
        '%Y-%m-%dT%H:%M:%S%z',        # '2023-10-23T19:07:17+0300'
        '%Y-%m-%dT%H:%M:%S%z',        # '2023-10-23T19:07:17+03:00'
        # Добавьте здесь другие форматы, которые вам нужны
    ]

    for fmt in formats:
        try:
            published_at_dt = datetime.strptime(published_at_str, fmt)
            if website_id in [32, 33]:
                published_at_dt -= timedelta(hours=3)
            return published_at_dt.strftime('%Y-%m-%d %H:%M:%S%z')
        except ValueError:
            pass

    # Попытка разобрать формат RFC 2822, например, "Wed, 02 Oct 2002 13:00:00 GMT"
    try:
        tuple_time = parsedate_tz(published_at_str)
        if tuple_time is not None:
            dt = datetime.fromtimestamp(mktime_tz(tuple_time), ZoneInfo('UTC'))
            if website_id in [32, 33]:
                dt -= timedelta(hours=3)
            return dt
    except Exception:
        pass

    # Если все попытки неудачны, возвращаем None или можно выбросить исключение
    return published_at_str


def get_resource(url):
    headers = get_headers()
    try:
        response = requests.get(url, headers=headers, timeout=15)
    except (requests.exceptions.ConnectTimeout, requests.exceptions.Timeout):
        try:
            response = requests.get(url, timeout=10)
        except (requests.exceptions.ConnectTimeout, requests.exceptions.Timeout):
            raise Exception("Timed out")
    response.raise_for_status() 
    return response.text


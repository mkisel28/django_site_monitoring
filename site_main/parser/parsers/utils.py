import html
import requests
from datetime import datetime, timedelta

def clean_html_entities(input_str: str) -> str:
    """Преобразует HTML-сущности в их фактические символы."""
    return html.unescape(input_str)




def format_date(published_at_str, website_id):

    published_at_str = published_at_str.replace("GMT", "+0000")

    formats = [
        '%a, %d %b %Y %H:%M:%S %z',   # для формата 'Mon, 23 Oct 2023 19:07:17 +0300'
        '%d %b %Y %H:%M:%S %z'       # для формата '23 Oct 2023 18:52:33 +0330'
    ]

    for fmt in formats:
        try:
            published_at_dt = datetime.strptime(published_at_str, fmt)
           
            if website_id in [32, 33]:
                published_at_dt -= timedelta(hours=3)
            return published_at_dt.strftime('%Y-%m-%d %H:%M:%S%z')
        except ValueError:
            pass  # Продолжаем следующую попытку разбора

    # Если все попытки разбора не удалось, возвращаем исходную строку
    return published_at_str


def get_resource(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = requests.get(url, headers=headers)
    response.raise_for_status() 
    return response.text


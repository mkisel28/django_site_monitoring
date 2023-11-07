import requests
from bs4 import BeautifulSoup
import feedparser


def get_headers():
    return {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
     

available_languages = {'afrikaans': 'af', 'albanian': 'sq', 'amharic': 'am', 'arabic': 'ar',
                       'armenian': 'hy', 'assamese': 'as', 'aymara': 'ay', 'azerbaijani': 'az',
                       'bambara': 'bm', 'basque': 'eu', 'belarusian': 'be', 'bengali': 'bn',
                       'bhojpuri': 'bho', 'bosnian': 'bs', 'bulgarian': 'bg',
                       'catalan': 'ca', 'cebuano': 'ceb', 'chichewa': 'ny',
                       'chinese (simplified)': 'zh-CN', 'chinese (traditional)': 'zh-TW',
                       'corsican': 'co', 'croatian': 'hr', 'czech': 'cs', 'danish': 'da',
                       'dhivehi': 'dv', 'dogri': 'doi', 'dutch': 'nl', 'english': 'en',
                       'esperanto': 'eo', 'estonian': 'et', 'ewe': 'ee', 'filipino': 'tl',
                       'finnish': 'fi', 'french': 'fr', 'frisian': 'fy', 'galician': 'gl',
                       'georgian': 'ka', 'german': 'de', 'greek': 'el', 'guarani': 'gn',
                       'gujarati': 'gu', 'haitian creole': 'ht', 'hausa': 'ha', 'hawaiian': 'haw',
                       'hebrew': 'iw', 'hindi': 'hi', 'hmong': 'hmn', 'hungarian': 'hu',
                       'icelandic': 'is', 'igbo': 'ig', 'ilocano': 'ilo', 'indonesian': 'id',
                       'irish': 'ga', 'italian': 'it', 'japanese': 'ja', 'javanese': 'jw',
                       'kannada': 'kn', 'kazakh': 'kk', 'khmer': 'km', 'kinyarwanda': 'rw',
                       'konkani': 'gom', 'korean': 'ko', 'krio': 'kri', 'kurdish (kurmanji)': 'ku',
                       'kurdish (sorani)': 'ckb', 'kyrgyz': 'ky', 'lao': 'lo', 'latin': 'la',
                       'latvian': 'lv', 'lingala': 'ln', 'lithuanian': 'lt', 'luganda': 'lg',
                       'luxembourgish': 'lb', 'macedonian': 'mk', 'maithili': 'mai', 'malagasy': 'mg',
                       'malay': 'ms', 'malayalam': 'ml', 'maltese': 'mt', 'maori': 'mi', 'marathi': 'mr',
                       'meiteilon (manipuri)': 'mni-Mtei', 'mizo': 'lus', 'mongolian': 'mn', 'myanmar': 'my',
                       'nepali': 'ne', 'norwegian': 'no', 'odia (oriya)': 'or', 'oromo': 'om', 'pashto': 'ps',
                       'persian': 'fa', 'polish': 'pl', 'portuguese': 'pt', 'punjabi': 'pa', 'quechua': 'qu',
                       'romanian': 'ro', 'russian': 'ru', 'samoan': 'sm', 'sanskrit': 'sa', 'scots gaelic': 'gd',
                       'sepedi': 'nso', 'serbian': 'sr', 'sesotho': 'st', 'shona': 'sn', 'sindhi': 'sd',
                       'sinhala': 'si', 'slovak': 'sk', 'slovenian': 'sl', 'somali': 'so', 'spanish': 'es',
                       'sundanese': 'su', 'swahili': 'sw', 'swedish': 'sv', 'tajik': 'tg', 'tamil': 'ta',
                       'tatar': 'tt', 'telugu': 'te', 'thai': 'th', 'tigrinya': 'ti', 'tsonga': 'ts',
                       'turkish': 'tr', 'turkmen': 'tk', 'twi': 'ak', 'ukrainian': 'uk', 'urdu': 'ur',
                       'uyghur': 'ug', 'uzbek': 'uz', 'vietnamese': 'vi', 'welsh': 'cy', 'xhosa': 'xh',
                       'yiddish': 'yi', 'yoruba': 'yo', 'zulu': 'zu'}


def find_rss_sitemap(url):
    headers = get_headers()

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        rss_links = soup.find_all('link', type="application/rss+xml")
        atom_links = soup.find_all('link', type="application/atom+xml")
        if not atom_links:
            atom_links = soup.find_all('link', type="application/rss+atom")
        sitemap_links = soup.find_all('link', type="application/xml")

        all_feeds = []
        all_feeds.extend([(link.get(
            'href'), f"RSS: {link.get('title', '')}:> {link.get('href')}") for link in rss_links])
        all_feeds.extend([(link.get(
            'href'), f"RSS: {link.get('title', '')}:> {link.get('href')}") for link in atom_links])
        all_feeds.extend([(link.get(
            'href'), f"SiteMap: {link.get('title', '')}:> {link.get('href')}") for link in sitemap_links])
        return all_feeds
    except requests.RequestException as e:
        print(f"Error: {e}")
        raise e


def get_rss_feed_info(url):
    headers = get_headers()
    feed = feedparser.parse(url, request_headers=headers)
    language = feed.get('feed', {}).get('language', 'Unknown')
    
    if language not in available_languages.values():
        language = '' 
    title = feed.get('feed', {}).get('title', 'Unknown')
    if not title:
        title = ''
    return language, title





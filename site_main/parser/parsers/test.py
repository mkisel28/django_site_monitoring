

# import html
# import requests
# from bs4 import BeautifulSoup
# from datetime import datetime


# def get_resource(url):
#     headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#     response = requests.get(url, headers=headers)

#     response.raise_for_status() 

#     return BeautifulSoup(response.text, 'xml')
# def parse(url):
#     try:
#       soup =  get_resource(url)
#     except Exception as e:
#         print(f"{url} - {e}")
#         return None
#     articles = []

#     for url in soup.find_all('url'):
#         title_tag = url.find('title')  
#         title = title_tag.text if title_tag else None

#         article_url = url.find('loc').text
#         lastmod_tag = url.find('lastmod')  if url.find('lastmod') else url.find('news:publication_date') 
#         lastmod = lastmod_tag.text if lastmod_tag else None 

#         articles.append(
#               {
#             'title': title,
#             'article_url': article_url,
#             'lastmod': lastmod
#               }
#             )
    
#     return articles

# url = "https://www.washingtonpost.com/arcio/news-sitemap/"

# print(parse(url))


def translate_text(from_lang, to_translate):
    translated_text = GoogleTranslator(source=from_lang, target='ru').translate(to_translate)
    return translated_text
from deep_translator import GoogleTranslator

a = "قالیباف: امروز فلسطین مساله اول جهان است"

print(translate_text("fa", a))
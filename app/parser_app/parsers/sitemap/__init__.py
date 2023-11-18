from ..utils import   clean_html_entities
from bs4 import BeautifulSoup
import logging


logger = logging.getLogger("parsers")


def parse(url, response):
    try:
      soup =  BeautifulSoup(response, 'xml')
    except Exception as e:
      logger.warning(f"Sitemap: Ошибка парсинга: {url} | {e}")
      return None
    articles = []
    
    for url in soup.find_all('url'):
        try:
          title_tag = url.find('title')  
          title = title_tag.text if title_tag else None

          article_url = url.find('loc').text
          lastmod_tag = url.find('lastmod')  if url.find('lastmod') else url.find('news:publication_date') 
          lastmod = lastmod_tag.text if lastmod_tag else None 

          articles.append(
                {
              'title': clean_html_entities(title),
              'article_url': article_url,
              'lastmod': lastmod
                }
            )
        except AttributeError as e:
           pass
    
    return articles[:100]
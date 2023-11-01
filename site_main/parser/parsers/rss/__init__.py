import xml.etree.ElementTree as ET
from ..utils import clean_html_entities
import logging
logger = logging.getLogger("controller")

def parse_atom(root):
    namespaces = {'atom': 'http://www.w3.org/2005/Atom'}

    articles = []
    for entry in root.findall('atom:entry', namespaces):
      try:
        title = entry.find('atom:title', namespaces).text
        article_url = entry.find("atom:link[@rel='alternate']", namespaces).get('href')
        published_at = entry.find('atom:published', namespaces).text
        articles.append({
                "title": clean_html_entities(title),
                "article_url": article_url,
                "lastmod": published_at
            })
      except AttributeError:
          pass
      except Exception as e:
          print(e)
    return articles[:100]


def parse(sitemap_url, response):
    try:
      xml_content = response
    except Exception as e:
        print(f"{sitemap_url} - {e}")
        return None
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
       logger.error(f"Error pars RSS: {sitemap_url} - {e}")
       return None
 
    # Поиск всех элементов <item>
    items = root.findall('.//item')
    if not items:
       items = parse_atom(root)
       return items if items else None

    articles = []
    
    for item in items:
        try:
          title = item.find('./title').text
          article_url = item.find('./link').text
          published_at = item.find('./pubDate').text
          articles.append({
              "title": clean_html_entities(title),
              "article_url": article_url,
              "lastmod": published_at
          })
        except AttributeError:
            pass
        except Exception as e:
           print(e)

        
    return articles[:100]


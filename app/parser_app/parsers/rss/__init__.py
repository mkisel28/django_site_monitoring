import xml.etree.ElementTree as ET
from ..utils import clean_html_entities
import logging
import feedparser

logger = logging.getLogger("parsers")

def append_article(articles, title, url, lastmod):
    try:
        if not title or not url:
            logger.warning(f"Title or URL is missing for an article. Title {title}, URL: {url[:20]}")
            return
        articles.append({
            "title": clean_html_entities(title),
            "article_url": url,
            "lastmod": lastmod
        })
    except AttributeError as e:
        logger.warning(f"Attribute error in append_article: {e}")
    except Exception as e:
        logger.error(f"Error appending article: {e}")

        
def feed_parse(sitemap_url):
    try:
        agent = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 YaBrowser/23.7.5.734 Yowser/2.5 Safari/537.36"}
        feed = feedparser.parse(sitemap_url, agent=str(agent['User-Agent']))

        if not feed.entries:
            feed = feedparser.parse(sitemap_url)
            
        articles = []
        for entry in feed.entries:
            append_article(articles, entry.title, entry.link, entry.published)

        return articles[:100] if articles else None
    except Exception as e:
        logger.error(f"Error in feed_parse: {e}")
        return None

def parse_atom(root):
    namespaces = {'atom': 'http://www.w3.org/2005/Atom'}
    articles = []

    for entry in root.findall('atom:entry', namespaces):
        try:
            title = entry.find('atom:title', namespaces).text
            article_url = entry.find("atom:link[@rel='alternate']", namespaces).get('href')
            published_at = entry.find('atom:published', namespaces).text
            append_article(articles, title, article_url, published_at)

        except AttributeError:
            pass
        except Exception as e:
            raise(e)

    return articles[:100] if articles else None

def parse_rss(items):
    articles = []
    for item in items:
        try:
            title = item.find('./title').text
            article_url = item.find('./link').text
            published_at = item.find('./pubDate').text
            append_article(articles, title, article_url, published_at)
        except AttributeError:
            pass
        except Exception as e:
            raise(e)
    return articles[:100]


def parse(sitemap_url, response):
    try:
        root = ET.fromstring(response)
        items = root.findall('.//item')
        if not items:
            items = parse_atom(root)
            return items
        return parse_rss(items)
    except ET.ParseError:
        return feed_parse(sitemap_url)
    except Exception as e:
        logger.warning(f"RSS: Не удалось спарсить сайт {sitemap_url}: {e}")
        return None


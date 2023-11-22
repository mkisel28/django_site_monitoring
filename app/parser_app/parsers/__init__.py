import logging
import json
from .utils import   get_resource
from . import sitemap, rss


logger = logging.getLogger("parsers")

def PARSERS():
    with open('./parsers/parsers.json', 'r') as f:
        url_to_parser_name = json.load(f)

    parsers_link = {
        url: globals()[parser_name]
        for url, parser_name in url_to_parser_name.items()
        }
    
    return parsers_link



def parse(base_url, sitemap_url):
    try:
        response = get_resource(sitemap_url)
    except Exception as e:
        logger.error(f"Ошибка запроса к сайту: {sitemap_url} | {e}")
        return None
    
    try:
        parsed_data = rss.parse(sitemap_url, response) or sitemap.parse(sitemap_url, response)
    except Exception as e:
        logger.error(f"Error during parsing data from {sitemap_url}: {e}")
        return None

    return parsed_data



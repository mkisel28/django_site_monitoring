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
        logger.error(f"Error parsing sitemapping: {sitemap_url} | {e}")
        return None
    
    parsed_data = rss.parse(sitemap_url, response)

    if not parsed_data:
        parsed_data = sitemap.parse(sitemap_url, response)
    
    if not parsed_data:
        return None
        parser = PARSERS().get(base_url)
        if parser:
            parsed_data = parser.parse(sitemap_url, response)
        else: return None

    return parsed_data




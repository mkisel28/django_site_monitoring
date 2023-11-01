import requests
from bs4 import BeautifulSoup
import sqlite3


def get_resource(url):
    response = requests.get(url)
    response.raise_for_status() 
    return BeautifulSoup(response.text, 'xml')


def fetch_sitemap_data(url):
    soup =  get_resource(url)
    urls_data = []

    for url in soup.find_all('url'):
        title_tag = url.find('title')  
        title = title_tag.text if title_tag else None

        article_url = url.find('loc').text
        lastmod_tag = url.find('lastmod')  if url.find('lastmod') else url.find('news:publication_date') 
        lastmod = lastmod_tag.text if lastmod_tag else None 

        urls_data.append((title, article_url, lastmod))
    
    return urls_data

def save_to_db(data, db_name='sitemap_data.db'):
    # Создание или подключение к базе данных
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # # Создаем таблицу, если она не существует
    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS sitemap_data (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         title TEXT,
    #         url TEXT UNIQUE,
    #         published_at TEXT
    #     )
    # ''')

    for entry in data:
        try:
            cursor.execute('''
                INSERT INTO sitemap_data (title, url, published_at)
                VALUES (?, ?, ?)
            ''', entry)
        except sqlite3.IntegrityError:
            pass
            # print(f"URL {entry[1]} уже существует в БД.")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    sitemap_url = "https://www.dw.com/ru/news-sitemap.xml"
    data = fetch_sitemap_data(sitemap_url)
    save_to_db(data)
import time
import psycopg2
from classificator import classify

conn_params = {
    'dbname': 'website_parsing',
    'user': 'postgres',
    'password': 'Maksim2001',
    'host': 'db'
}


            
def classify_articles():
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, eng_title FROM main_article WHERE category IS NULL AND eng_title IS NOT NULL;")
            articles = cur.fetchall()
            for article_id, title in articles:
                category = classify(title)
                cur.execute("UPDATE main_article SET category = %s WHERE id = %s;", (category, article_id))
        conn.commit()

if __name__ == "__main__":
    while True:
        classify_articles()
        time.sleep(3)







# На случай если нужно будет обновить всю БД

# import concurrent.futures
# from deep_translator import GoogleTranslator

# def translate_text_to_eng(from_lang: str, to_translate: str) -> str:
#     """
#     Переводит текст на английский язык, с повторными попытками в случае ошибок.

#     Args:
#     - from_lang: Исходный язык текста.
#     - to_translate: Текст для перевода.

#     Returns:
#     - Переведенный текст.
#     """
#     MAX_RETRIES = 10
#     for i in range(MAX_RETRIES):
#         try:
#             translated_text = GoogleTranslator(source=from_lang.lower(), target="en").translate(
#                 to_translate
#             )

#             return translated_text
#         except Exception:
#             print(f"Попытка перевода №{i+1}. Ошибка перевода.")
#             time.sleep(1)
  

# import time




# def start_first_migrate_for_get_category():
#   with psycopg2.connect(**conn_params) as conn:
#       with conn.cursor() as cursor:
#           cursor.execute("""
#               UPDATE main_article SET eng_title = title
#               FROM main_website
#               WHERE main_article.website_id = main_website.id AND main_website.language = 'en' AND main_article.eng_title IS NULL
#           """)
#           conn.commit()
#   with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
#     future_to_article = {executor.submit(translate_text_to_eng, article[2], article[1]): article for article in articles_to_translate}
#     for future in concurrent.futures.as_completed(future_to_article):
#         article = future_to_article[future]
#         try:
#             eng_title = future.result()
#             update_article(article[0], eng_title)
#         except Exception as exc:
#             print(f'Article id {article[0]} generated an exception: {exc}')  
        
# def update_article(article_id, eng_title):
#     with psycopg2.connect(**conn_params) as conn:
#         with conn.cursor() as cursor:
#             cursor.execute("UPDATE main_article SET eng_title = %s WHERE id = %s", (eng_title, article_id))
#         conn.commit()

# if __name__ == "__main__":
#     # classify_articles()

#   with psycopg2.connect(**conn_params) as conn:
#     with conn.cursor() as cursor:
#       cursor.execute("""
#               SELECT a.id, a.title, w.language 
#               FROM main_article a
#               JOIN main_website w ON a.website_id = w.id 
#               WHERE a.eng_title IS NULL AND w.language != 'en'
#           """)
#       articles_to_translate = cursor.fetchall()
    
#   if len(articles_to_translate) == 0:
#       print("Nothing to translate")
#   else:
#     start_first_migrate_for_get_category()
    

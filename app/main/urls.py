from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
     path('websites/', views.website_list, name='website_list'),
     path('websites/<int:website_id>/articles/',
          views.website_articles, name='website_articles'),
     path('search/', views.search, name='search'),
     path('live/', views.live_all, name='live_all'),
     path('country/', views.country_monitoring, name='country_monitoring'),

     path('country/<str:country_code>/', views.country_articles, name='country_articles'),
     path('all_favourite_country/', views.all_favourite_country, name='all_favourite_country'),



     path('add_favorite/<int:website_id>/',
          views.add_website_to_favorites_api, name='add_favorite'),
     path('remove_favorite/<int:website_id>/',
          views.remove_website_from_favorites_api, name='remove_favorite'),
     path('add_favorite_country/<str:country_code>/', views.add_country_to_favorites_api, name='add_favorite_country'),
     path('remove_favorite_country/<str:country_code>/', views.remove_country_from_favorites_api, name='remove_favorite_country'),

     # path('api/websites/<int:website_id>/articles/',
     #      views.api_article_list, name='api_article_list'),
     path('api/websites/',
          views.api_article_list, name='api_website_article_list'),
          
     path('api/live_all/', views.get_all_live_articles_api, name='api_live_all'),
     path('api/articles_from_favourite_countries/', views.get_favorite_countries_articles_api, name='api_articles_from_favourite_countries'),

     #path('api/api_country_articles/', views.api_country_articles, name='api_country_articles'),
     # path('api/articles_for_word/<int:word_id>/', views.articles_for_word, name='articles_for_word'),
     path('api/articles_for_related_data/<str:data_type>/<int:data_id>/', views.articles_for_related_data, name='articles_for_related_data'),


     path('api/get_tab_data/' , views.get_tab_data_api, name='get_data_tab'),
     path('api/test/', views.test, name='api_country_articles'),


    # path('api/websites/', views.website_api, name='api_article_list'),
]

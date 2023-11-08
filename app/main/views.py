from typing import List, Dict, Any

from django.db.models import OuterRef, Exists
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .models import Website, Country, Article, Word, Configuration, TrackedWord, TrackedWordMention
from django.db.models import Q

from utils.date_helpers import apply_date_filter
from utils.request_helpers import get_int_list_from_request
from utils.query_helpers import build_search_query
from utils.text_helpers import create_articles

# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync

# def new_post_published(post):
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(
#         "post_notifications", {
#             "type": "post_notification",
#             "message": f"A new post titled '{post}' has been published!"
#         }
#     )

# def index(request):
#     new_post_published("Test post")
#     return render(request, 'main/index.html')


@login_required(login_url="/")
def website_list(request):
    """
    Отображает страницу со списком всех сайтов, отсортированных по времени последнего сканирования.
    """
    websites = Website.objects.all().order_by('-last_scraped')
    return render(request, 'main/website_list.html', {'websites': websites})


@login_required(login_url="/")
def live_all(request):
    """
    Отображает страницу со всеми статьями в реальном времени.
    """
    config = Configuration.objects.first()
    TOP_COUNT = config.top_words_count
    
    words = Word.objects.order_by('-id')[:TOP_COUNT]

    tracked_words = TrackedWord.objects.filter(user=request.user)

    # Создаем список словарей с каждым словом и его количеством упоминаний
    tracked_word_with_counts = []
    for tracked_word in tracked_words:
        mentions_count = TrackedWordMention.objects.filter(
            word=tracked_word).count()
        tracked_word_with_counts.append({
            'word': tracked_word,
            'count': mentions_count
        })
    return render(request, 'main/live.html', {'articles': None,
                                              'words': words[::-1],
                                              "tracked_word_with_counts": tracked_word_with_counts})


@login_required(login_url="/")
def all_favourite_country(request):
    """
    Отображает страницу с избранными странами пользователя.
    """
    return render(request, 'main/all_favourite_country.html')


@login_required(login_url="/")
def search(request):
    """
    Отображает страницу со статьями на основе поискового запроса и фильтров стран пользователя.
    """
    search_post = request.GET.get('search', '').lower().split()
    country_filters = request.GET.getlist(
        'countries')  # Получаем список выбранных стран
    articles = Article.objects.filter(
        Q(website__user=None) | Q(website__user=request.user)
    )
    q_objects = build_search_query(search_post)

    articles = articles.filter(q_objects)

    # Если выбраны страны, фильтруем по ним
    if country_filters:
        # Получаем все страны одним запросом
        all_countries = Country.objects.filter(
            code__in=country_filters).values('code', 'name')
        # Создаем словарь {code: name}
        country_dict = {country['code']: country['name']
                        for country in all_countries}
        # Используем этот словарь для получения имен стран
        selected_countries = ', '.join(
            [country_dict[code] for code in country_filters])

        articles = articles.filter(website__country__code__in=country_filters).order_by("-published_at").values(
            'id', 'title', 'title_translate', 'url', 'published_at', 'website__name', 'website__country__name')
    else:
        selected_countries = None
        articles = articles.order_by("-published_at").values('id', 'title', 'title_translate',
                                                             'url', 'published_at', 'website__name', 'website__country__name')
    total_articles = len(articles)

    articles = create_articles(articles[:1000])

    countries = Country.objects.all()

    return render(request, 'main/search.html', {
        'articles': articles,
        'text': ' '.join(search_post),
        'total_articles': total_articles,
        'countries': countries,
        'selected_countries': selected_countries
    })


@login_required(login_url="/")
def country_monitoring(request):
    """
    Отображает страницу с мониторингом по странам.
    """
    config = Configuration.objects.first()
    TOP_COUNT = config.top_words_count

    favorite_countries = request.user.favorite_countries.all()
    other_countries = Country.objects.exclude(id__in=favorite_countries)

    favorite_sites = Website.objects.filter(
        Q(user=None) | Q(user=request.user),
        favorited_by=request.user
    ).order_by('country__id')

    other_sites = Website.objects.filter(
        Q(user=None) | Q(user=request.user)
    ).exclude(
        favorited_by=request.user).order_by('country__id')

    words = Word.objects.order_by('-id')[:TOP_COUNT]

    tracked_words = TrackedWord.objects.filter(user=request.user)

    # Создаем список словарей с каждым словом и его количеством упоминаний
    tracked_word_with_counts = []
    for tracked_word in tracked_words:
        mentions_count = TrackedWordMention.objects.filter(
            word=tracked_word).count()
        tracked_word_with_counts.append({
            'word': tracked_word,
            'count': mentions_count
        })

    context = {
        'favorite_countries': favorite_countries,
        'other_countries': other_countries,
        'favorite_sites': favorite_sites,
        'other_sites': other_sites,
        'words': words[::-1],
        "tracked_word_with_counts": tracked_word_with_counts
    }

    return render(request, 'main/country_monitoring.html', context)


@login_required(login_url="/")
def country_articles(request, country_code):
    """
    Отображает страницу со статьями, относящимися к конкретной стране, определенной ее кодом.
    """
    country = get_object_or_404(Country, code=country_code)
    return render(request, 'main/country_articles.html', {'country': country})


################ API##################


@login_required(login_url="/")
def api_country_articles(request):
    """
    API-точка, которая возвращает статьи, относящиеся к конкретной стране.
    """
    country_code = request.GET.get('country')
    only_favorites = request.GET.get('only_favorites')

    country = get_object_or_404(Country, code=country_code)
    articles = Article.objects.annotate(
        is_favorite=Exists(
            Website.objects.filter(
                id=OuterRef('website_id'),
                favorited_by=request.user
            )
        )
    ).filter(website__country=country
             ).order_by('-published_at'
                        ).values('id', 'title', 'title_translate', 'url', 'published_at', 'website__name', 'website__id', 'website__country__name', 'is_favorite')

    if only_favorites:
        articles = articles.filter(website__favorited_by=request.user)[:100]
        articles = create_articles(articles)[::-1]

    else:
        articles = create_articles(articles[:100])[::-1]
    data = {
        'articles': list(articles),
    }

    return JsonResponse(data)


######### ОСНАВНАЯ API-ТОЧКА############
@login_required(login_url="/")
def api_article_list(request):
    """
    API-точка, которая возвращает список статей для конкретного сайта по его ID.
    Главная страница HTML: website_list.html
    """
    # articles = Article.objects.filter(website_id=website_id).order_by(
    #     "-published_at").values('id', 'title', 'title_translate', 'url', 'published_at')[:3]

    # articles = create_articles(articles)[::-1]
    # return JsonResponse({'articles': list(articles)})

    website_ids = request.GET.getlist('website_ids[]')

    all_articles = {}

    for website_id in website_ids:

        articles = Article.objects.filter(
            Q(website__user=None) | Q(website__user=request.user),
            website_id=website_id
        ).order_by("-published_at").values('id', 'title', 'title_translate', 'url', 'published_at')[:3]
        all_articles[website_id] = create_articles(articles)[::-1]

    return JsonResponse({'websites': all_articles})


@login_required(login_url="/")
def get_favorite_countries_articles_api(request):
    """
    API-точка, которая возвращает статьи из избранных стран пользователя.
    """
    # Получаем избранные страны пользователя
    only_favorites = request.GET.get('only_favorites')

    favourite_countries = request.user.favorite_countries.all()

    # Получаем статьи из этих стран
    articles = Article.objects.annotate(
        is_favorite=Exists(
            Website.objects.filter(
                id=OuterRef('website_id'),
                favorited_by=request.user
            )
        )
    ).filter(website__country__in=favourite_countries).order_by("-published_at").values(
        'id', 'title', 'title_translate', 'url', 'published_at', 'website__name', 'website__id', 'website__country__name', 'is_favorite'
    )
    articles = articles.filter(
        Q(website__user=None) | Q(website__user=request.user)
    )
    if only_favorites:
        articles = articles.filter(website__favorited_by=request.user)[:100]
        articles = create_articles(articles)[::-1]

    else:
        articles = create_articles(articles[:100])[::-1]

    return JsonResponse({'articles': list(articles)})


@login_required(login_url="/")
def get_all_live_articles_api(request):
    """
    API-точка, которая возвращает все статьи в реальном времени.
    """
    only_favorites = request.GET.get('only_favorites')
    articles = Article.objects.annotate(
        is_favorite=Exists(
            Website.objects.filter(
                id=OuterRef('website_id'),
                favorited_by=request.user
            )
        )
    ).order_by("-published_at").values(
        'id', 'title', 'title_translate', 'url', 'published_at', 'website__name', 'website__id', 'website__country__name', 'is_favorite'
    )
    articles = articles.filter(
        Q(website__user=None) | Q(website__user=request.user)
    )
    if only_favorites:
        articles = articles.filter(website__favorited_by=request.user)[:100]
    else:
        articles = articles[:100]
    articles = create_articles(articles)[::-1]
    return JsonResponse({'articles': list(articles)})


########## ОСТАЛЬНАЯ API-ТОЧКИ############
@login_required(login_url="/")
def articles_for_related_data(request, data_id, data_type):
    """
    Получает статьи, связанные с определенным типом данных (словом или отслеживаемым словом) на основе
    предоставленных фильтров запроса.

    Args:
    - request (HttpRequest): Запрос от клиента.
    - data_id (int): ID слова или отслеживаемого слова.
    - data_type (str): Тип данных - "word" или "track".

    Filters:
    - date (str): Фильтр по дате ("today", "week", "month").
    - count (int): Количество возвращаемых статей.
    - countries (str): Список ID стран, разделенных запятыми.
    - websites (str): Список ID веб-сайтов, разделенных запятыми.

    Returns:
    - JsonResponse: Статьи, соответствующие условиям фильтра, или сообщение об ошибке.

    Exepctions:
    - 400: Если тип данных не является действительным или не найдены соответствующие статьи.
    """
    date_filter = request.GET.get('date')
    count_filter = int(request.GET.get('count', 1000))
    countries_filter = get_int_list_from_request(request, 'countries')
    websites_filter = get_int_list_from_request(request, 'websites')

    if data_type == "word":
        word = get_object_or_404(Word, id=data_id)
        base_query = word.articles.all()
        date_filter, count_filter, countries_filter, websites_filter = None, 100, None, None
    elif data_type == "track":
        tracked_word = get_object_or_404(TrackedWord, id=data_id)
        base_query = Article.objects.filter(mentions__word=tracked_word)
    else:
        return JsonResponse({'error': 'Invalid data type'}, status=400)

    base_query = apply_date_filter(base_query, date_filter)

    if countries_filter:
        base_query = base_query.filter(
            website__country__id__in=countries_filter)

    if websites_filter:
        base_query = base_query.filter(website__id__in=websites_filter)

    # Применение аннотаций и возвращение результатов
    articles = base_query.filter(
        Q(website__user=None) | Q(website__user=request.user)
    ).annotate(
        is_favorite=Exists(
            Website.objects.filter(
                id=OuterRef('website_id'),
                favorited_by=request.user
            )
        )
    ).values('id',
             'title',
             'title_translate',
             'url',
             'website__name',
             'website__id',
             'website__country__name',
             'published_at',
             'is_favorite')[:count_filter]

    articles = create_articles(articles)[::-1]

    if len(articles) == 0:
        return JsonResponse({'error': 'Ничего не найдено'})

    return JsonResponse({'articles': list(articles)})


@login_required(login_url="/")
def website_articles(request, website_id):
    """
    Отображает страницу со списком статей для конкретного сайта по его ID.
    """
    articles = Article.objects.filter(website_id=website_id).order_by(
        "-published_at").values('id', 'title', 'title_translate', 'url', 'published_at')

    articles = create_articles(articles)
    return render(request, 'main/article_list.html', {'articles': articles})


@login_required(login_url="/")
def add_website_to_favorites_api(request, website_id):
    """
    API-точка, которая позволяет пользователю добавить конкретный сайт в избранное.
    """
    try:
        website = get_object_or_404(Website, id=website_id)
        website.favorited_by.add(request.user)
        return JsonResponse({"status": "added", "message": "Added to favorites"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@login_required(login_url="/")
def remove_website_from_favorites_api(request, website_id):
    """
    API-точка, которая позволяет пользователю удалить конкретный сайт из избранного.
    """
    try:
        website = get_object_or_404(Website, id=website_id)
        website.favorited_by.remove(request.user)
        return JsonResponse({"status": "removed", "message": "Removed from favorites"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@login_required(login_url="/")
def add_country_to_favorites_api(request, country_code):
    """
    API-точка, которая позволяет пользователю добавить конкретную страну в избранное по ее коду.
    """
    try:
        country = Country.objects.get(code=country_code)
        # добавляем страну в избранное для текущего пользователя
        request.user.favorite_countries.add(country)
        return JsonResponse({"status": "added", "message": "Страна добавлена в избранное!"})
    except Country.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Страна не найдена!"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


@login_required(login_url="/")
def remove_country_from_favorites_api(request, country_code):
    """
    API-точка, которая позволяет пользователю удалить конкретную страну из избранного по ее коду.
    """
    try:
        country = Country.objects.get(code=country_code)
        # удаляем страну из избранного для текущего пользователя
        request.user.favorite_countries.remove(country)
        return JsonResponse({"status": "removed", "message": "Страна удалена из избранного!"})
    except Country.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Страна не найдена!"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


########## ОСТАЛЬНАЯ API-ТОЧКИ############

@login_required(login_url="/")
def test(request):
    """
    Объединенная API-точка для получения статей на основе различных критериев.
    """
    country_code = request.GET.get('country')
    website_id = request.GET.get('website_id')
    only_favorites = request.GET.get('only_favorites')
    live = request.GET.get('live')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if country_code:
        country = get_object_or_404(Country, code=country_code)
        articles = Article.objects.filter(website__country=country)

    elif website_id:
        articles = Article.objects.filter(website_id=website_id)

    elif live:
        articles = Article.objects.all()

    else:
        favourite_countries = request.user.favorite_countries.all()
        articles = Article.objects.filter(
            website__country__in=favourite_countries)
    # Фильтрация статей на основе сайтов с website.user = None или сайтов привязанных к пользователю
    articles = articles.filter(
        Q(website__user=None) | Q(website__user=request.user)
    )
    articles = articles.annotate(
        is_favorite=Exists(
            Website.objects.filter(
                id=OuterRef('website_id'),
                favorited_by=request.user
            )
        )
    )
    if start_date:
        articles = articles.filter(published_at__gte=start_date)
    if end_date:
        articles = articles.filter(published_at__lte=end_date)

    if only_favorites:
        articles = articles.filter(website__favorited_by=request.user)

    articles = articles.order_by("-published_at").values(
        'id',
        'title',
        'title_translate',
        'url',
        'published_at',
        'website__name',
        'website__id',
        'website__country__name',
        'is_favorite'
    )[:10]

    articles = create_articles(articles)[::-1]

    return JsonResponse({'articles': list(articles)})

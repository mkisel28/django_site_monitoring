import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from utils.request_helpers import get_int_list_from_request
from parser_app.parsers.search.test import find_rss_sitemap, get_rss_feed_info
from main.models import Article, TrackedWord, TrackedWordMention
from .forms import RegistrationForm, TrackedWordForm, AddWebsiteForm, SitemapChoiceForm
from django.http import HttpResponseBadRequest
from django.template.loader import render_to_string
from main.models import Country, Website
from django.db.models import Q
from .models import Tab, Task
from django.views.decorators.http import require_POST

from django.db.utils import IntegrityError


def user_login(request):
    if request.user.is_authenticated:
        return redirect("/websites")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse(
                    {
                        "status": "success",
                        "message": f"Привет, {username}! Вы успешно вошли в систему.",
                    }
                )
            else:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Неправильное имя пользователя или пароль",
                    },
                    status=401,
                )
        else:
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            return JsonResponse(
                {
                    "status": "success",
                    "message": f"Аккаунт создан для {username}! Теперь вы можете войти в систему.",
                }
            )
        else:
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required(login_url="/")
def dashboard(request):
    words = TrackedWord.objects.filter(user=request.user).order_by("-id")
    countries = Country.objects.all()
    websites = Website.objects.filter(Q(user=request.user) | Q(user=None))

    # Создаем список словарей с каждым словом и его количеством упоминаний
    words_with_counts = []
    for word in words:
        mentions_count = TrackedWordMention.objects.filter(word=word).count()
        words_with_counts.append({"word": word, "count": mentions_count})

    paginator = Paginator(words_with_counts, 5)  # Показывать 10 слов на страницу
    page_number = request.GET.get("page")
    words_with_counts = paginator.get_page(page_number)
    form = TrackedWordForm()
    
    total_website_count = websites.count()
    total_countries_count = countries.count()
    total_tasks_count = Task.objects.filter(user=request.user).count()

    return render(
        request,
        "users/dashboard.html",
        {
            "form": form,
            "words_with_counts": words_with_counts,
            "countries": countries,
            "websites": websites,
            "total_website_count": total_website_count,
            "total_countries_count": total_countries_count,
            "total_tasks_count": total_tasks_count,
        },
    )


@login_required(login_url="/")
def dashboard_settings(request):
    return render(request, "users/dashboard_settings.html")


def dashboard_trackword(request):
    words = TrackedWord.objects.filter(user=request.user).order_by("-id")

    words_with_counts = []
    for word in words:
        mentions_count = TrackedWordMention.objects.filter(word=word).count()
        words_with_counts.append({"word": word, "count": mentions_count})
    # Настройка пагинации
    paginator = Paginator(words_with_counts, 10)  # Показывать 10 слов на страницу
    page_number = request.GET.get("page")
    words_with_counts = paginator.get_page(page_number)

    form = TrackedWordForm()
    return render(
        request,
        "users/dashboard_track_word.html",
        {"form": form, "words_with_counts": words_with_counts},
    )


def dashboard_collection(request):
    countries = Country.objects.all()
    websites = Website.objects.filter(Q(user=request.user) | Q(user=None))
    my_tabs = Tab.objects.filter(user=request.user)

    all_websites = websites
    all_countries = countries
    all_tracked_words = TrackedWord.objects.filter(user=request.user)
    print(all_tracked_words)

    return render(
        request,
        "users/dashboard_collection.html",
        {
            "countries": countries,
            "websites": websites,
            "my_tabs": my_tabs,
            "all_websites": all_websites,
            "all_countries": all_countries,
            "all_tracked_words": all_tracked_words,
        },
    )


def dashboard_sites(request):
    return render(request, "users/dashboard_sites.html")


@login_required(login_url="/")
def api_manage_tab(request):
    if request.method == "POST":
        data = json.loads(request.body)

        tab = Tab.objects.create(user=request.user, name=data["name"])

        for website_id in data.get("websites", []):
            print(type(int(website_id)), int(website_id))
            tab.add_website(int(website_id))
        for country_id in data.get("countries", []):
            tab.add_country(country_id)
        for tracked_word_id in data.get("tracked_words", []):
            tab.add_tracked_word(tracked_word_id)
        return JsonResponse(
            {"status": "success", "message": "Вкладка успешно создана."}
        )


@login_required(login_url="/")
def fetch_sitemaps(request):
    if request.method == "POST":
        url = request.POST.get("url")
        request.session["url"] = url
        try:
            sitemaps = find_rss_sitemap(url)

            # HTML с формой для этапа 2
            form_html = render_to_string(
                "users/module/sitemap_form.html",
                {"sitemaps": sitemaps},
                request=request,
            )
            return JsonResponse({"form_html": form_html})

        except Exception as e:
            print(e)
            return HttpResponseBadRequest(str(e))

    return HttpResponseBadRequest("Invalid request")


@login_required(login_url="/")
def fetch_website_details(request):
    if request.method == "POST":
        sitemap_url = request.POST.get("sitemap_url")
        try:
            language, name = get_rss_feed_info(sitemap_url)
            url = request.session.get("url", [])
            countries = Country.objects.all()

            website_data = {
                "base_url": url,
                "sitemap_url": sitemap_url,
                "name": name,
                "language": language,
            }
            # HTML с формой для этапа 3
            form_html = render_to_string(
                "users/module/path_to_sitemap_form_template.html",
                {"website_data": website_data, "countries": countries},
                request=request,
            )
            return JsonResponse({"form_html": form_html})

        except Exception as e:
            return HttpResponseBadRequest(str(e))

    return HttpResponseBadRequest("Invalid request")


@login_required(login_url="/")
def save_website(request):
    if request.method == "POST":
        form = AddWebsiteForm(request.POST)
        if form.is_valid():
            website = form.save(commit=False)
            if request.user.is_staff:
                website.user = None
            else:
                website.user = request.user
            website.save()
            return JsonResponse(
                {"status": "success", "message": "Сайт успешно сохранен."}
            )
        else:
            return JsonResponse({"status": "error", "message": form.errors})

    return JsonResponse({"error": "Invalid method."})


@login_required(login_url="/")
def toggle_telegram_notifications(request):
    if request.method == "POST":
        user_profile = request.user.userprofile

        # Обновляем значение chat_id
        telegram_chat_id = request.POST.get("telegram_chat_id")
        if telegram_chat_id:
            user_profile.telegram_chat_id = telegram_chat_id

        telegram_notifications = request.POST.get("telegram_notifications") == "on"
        user_profile.telegram_notifications = telegram_notifications
        user_profile.save()

        messages.success(request, "Настройки уведомлений обновлены.")
        return redirect("users:manage_tracked_words")

    return redirect("users:manage_tracked_words")


@login_required(login_url="/")
def add_word_api(request):
    if request.method == "POST":
        form = TrackedWordForm(request.POST)
        if form.is_valid():
            try:
                word = form.save(commit=False)
                word.user = request.user
                word.save()
            except IntegrityError as e:
                return JsonResponse({"status": "error", "errors": 'У вас уже есть такое слово'})

            mentions_count = TrackedWordMention.objects.filter(word=word).count()

            return JsonResponse(
                {
                    "status": "success",
                    "word_id": word.id,
                    "word_text": word.keyword,
                    "count": mentions_count,
                }
            )
        else:
            return JsonResponse({"status": "error", "errors": form.errors})
    return JsonResponse({"status": "error", "errors": "Invalid request"})


@login_required(login_url="/")
def delete_word_api(request, word_id):
    try:
        word = TrackedWord.objects.get(id=word_id, user=request.user)
        word.delete()
        return JsonResponse({"status": "success"})

    except TrackedWord.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Word not found"})


@require_POST
@login_required(login_url="/")
def update_tab(request):
    try:
        data = request.POST
        tab_id = data.get("tab_id")

        try:
            selected_websites = list(map(int, data.getlist("websites[]")))
            selected_countries = list(map(int, data.getlist("countries[]")))
            selected_words = list(map(int, data.getlist("tracked_words[]")))
        except ValueError:
            return JsonResponse({"message": "Неверный формат данных"}, status=400)

        tab = Tab.objects.get(id=tab_id, user=request.user)

        # Обновление сайтов во вкладке
        tab.tab_websites.all().delete()
        for website_id in selected_websites:
            tab.add_website(website_id)

        # Обновление стран во вкладке
        tab.tab_countries.all().delete()
        for country_id in selected_countries:
            tab.add_country(country_id)

        # Обновление отслеживаемых слов во вкладке
        tab.tab_tracked_words.all().delete()
        for word_id in selected_words:
            tab.add_tracked_word(word_id)
        tab.save()

        return JsonResponse(
            {"message": "Данные вкладки успешно обновлены."}, status=200
        )

    except Tab.DoesNotExist:
        return JsonResponse({"error": "Вкладка не найдена."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




@login_required(login_url="/")
def api_task_create(request):
    if request.method == "POST":
        user = request.user
        article_id = request.POST.get('article_id')
        print(article_id)
        status = request.POST.get('status')
        priority = request.POST.get('priority')

        try:
            # Проверка, существует ли статья
            article = Article.objects.get(id=article_id)

            # Создание новой задачи
            task = Task.objects.create(
                user=user,
                article=article,
                status=status,
                priority=priority
            )
            task.save()


            return JsonResponse({'success': True})

        except Article.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Article not found'}, status=404)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url="/")   
def api_task_update(request):
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        status = request.POST.get('status')
        priority = request.POST.get('priority')

        # Проверка на существование задачи
        try:
            task = Task.objects.get(article_id=article_id, user=request.user)
            if status:
                task.status = status
            if priority:
                task.priority = priority
            task.save()
            return JsonResponse({'status': 'success', 'message': 'Задача обновлена'})
        except Task.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Задача не найдена'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Неверный запрос'}, status=400)


def api_get_all_tasks(request):

    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    
    tasks = Task.objects.filter(user=request.user)
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    # Рендеринг списка задач
    html = render_to_string('users/module/submodule/tasks_list.html', {'tasks': tasks})
    return JsonResponse({'html': html})

@login_required(login_url="/")
def api_task_info(request, task_id):
    try:
        task = Task.objects.get(article=task_id, user=request.user)
        return JsonResponse({
            'id': task.id,
            'article_id': task.article.id,
            'status': task.status,
            'priority': task.priority,
            'created_at': task.created_at,
            'updated_at': task.updated_at,
        })
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    
    
    
def api_tasks(request):
    tasks = Task.objects.all()
    data = list(tasks.values(
        'id', 'user__username', 'article__title', 'status', 'priority', 
        'created_at', 'updated_at'
    ))

    return JsonResponse(data, safe=False)
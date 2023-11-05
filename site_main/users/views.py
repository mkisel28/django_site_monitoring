
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


from parser_app.parsers.search.test import find_rss_sitemap, get_rss_feed_info
from main.models import TrackedWord, TrackedWordMention
from .forms import RegistrationForm, TrackedWordForm, AddWebsiteForm, SitemapChoiceForm
from django.http import HttpResponseBadRequest
from django.template.loader import render_to_string
from main.models import Country


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(
                request, f'Аккаунт создан для {username}! Теперь вы можете войти в систему.')
            return redirect('/')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def manage_tracked_words(request):
    words = TrackedWord.objects.filter(user=request.user)

    # Создаем список словарей с каждым словом и его количеством упоминаний
    words_with_counts = []
    for word in words:
        mentions_count = TrackedWordMention.objects.filter(word=word).count()
        words_with_counts.append({
            'word': word,
            'count': mentions_count
        })

    form = TrackedWordForm()
    return render(request, 'users/d.html', {'form': form, 'words_with_counts': words_with_counts})


def fetch_sitemaps(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        request.session['url'] = url
        try:
            sitemaps = find_rss_sitemap(url)

            # HTML с формой для этапа 2
            form_html = render_to_string(
                'users/module/sitemap_form.html',
                {'sitemaps': sitemaps},
                request=request
            )
            return JsonResponse({'form_html': form_html})

        except Exception as e:
            print(e)
            return HttpResponseBadRequest(str(e))

    return HttpResponseBadRequest("Invalid request")


def fetch_website_details(request):
    if request.method == 'POST':
        sitemap_url = request.POST.get('sitemap_url')
        try:
            language, name = get_rss_feed_info(sitemap_url)
            url = request.session.get('url', [])
            countries = Country.objects.all()

            website_data = {
                'base_url': url,
                'sitemap_url': sitemap_url,
                'name': name,
                'language': language
            }
            # HTML с формой для этапа 3
            form_html = render_to_string(
                'users/module/path_to_sitemap_form_template.html',
                {'website_data': website_data,
                 'countries': countries},
                request=request
            )
            return JsonResponse({'form_html': form_html})

        except Exception as e:
            return HttpResponseBadRequest(str(e))

    return HttpResponseBadRequest("Invalid request")


def save_website(request):
    if request.method == 'POST':
        form = AddWebsiteForm(request.POST)
        if form.is_valid():
            website = form.save(commit=False)
            if request.user.is_staff:  # Если пользователь - админ, то не привязываем сайт к пользователю
                website.user = None
            else:
                website.user = request.user
            website.save()
            del request.session['url']
            return JsonResponse({'status': 'success', 'message': 'Сайт успешно сохранен.'})
        else:
            return JsonResponse({'status': 'error', 'message': form.errors})

    return JsonResponse({'error': 'Invalid method.'})


@login_required
def toggle_telegram_notifications(request):
    if request.method == "POST":
        user_profile = request.user.userprofile

        # Обновляем значение chat_id
        telegram_chat_id = request.POST.get('telegram_chat_id')
        if telegram_chat_id:
            user_profile.telegram_chat_id = telegram_chat_id

        telegram_notifications = request.POST.get(
            'telegram_notifications') == 'on'
        user_profile.telegram_notifications = telegram_notifications
        user_profile.save()

        messages.success(request, 'Настройки уведомлений обновлены.')
        return redirect('users:manage_tracked_words')

    return redirect('users:manage_tracked_words')


@login_required
def add_word_api(request):
    if request.method == 'POST':
        form = TrackedWordForm(request.POST)
        if form.is_valid():
            word = form.save(commit=False)
            word.user = request.user
            word.save()
            mentions_count = TrackedWordMention.objects.filter(
                word=word).count()

            return JsonResponse({'status': 'success', 'word_id': word.id, 'word_text': word.keyword, 'count': mentions_count})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
def delete_word_api(request, word_id):
    try:
        word = TrackedWord.objects.get(id=word_id, user=request.user)
        word.delete()
        return JsonResponse({'status': 'success'})

    except TrackedWord.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Word not found'})

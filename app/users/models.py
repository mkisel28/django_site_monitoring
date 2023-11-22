from django.db import models
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from main.models import Country, TrackedWord, Website, Article

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.sessions.models import Session


class Tab(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tabs", verbose_name="Пользователь")
    name = models.CharField(max_length=255, verbose_name="Название вкладки")
    class Meta:
      verbose_name = "Вкладка"
      verbose_name_plural = "Вкладки"
      
    def __str__(self):
        return self.name
    # Метод для добавления сайта в вкладку
    def add_website(self, website_id):
        website = get_object_or_404(Website, pk=website_id)
        tab_website, created = TabWebsite.objects.get_or_create(tab=self, website=website)
        return tab_website

    # Метод для добавления страны в вкладку
    def add_country(self, country_id):
        country = get_object_or_404(Country, pk=country_id)
        tab_country, created = TabCountry.objects.get_or_create(tab=self, country=country)
        return tab_country

    # Метод для добавления отслеживаемого слова в вкладку
    def add_tracked_word(self, tracked_word_id):
        tracked_word = get_object_or_404(TrackedWord, pk=tracked_word_id)
        tab_tracked_word, created = TabTrackedWord.objects.get_or_create(tab=self, tracked_word=tracked_word)
        return tab_tracked_word
    
    # Получить все сайты, связанные с этой вкладкой
    def get_websites(self):
        return [tab_website.website for tab_website in self.tab_websites.all()]

    # Получить все страны, связанные с этой вкладкой
    def get_countries(self):
        return [tab_country.country for tab_country in self.tab_countries.all()]

    # Получить все отслеживаемые слова, связанные с этой вкладкой
    def get_tracked_words(self):
        return [tab_tracked_word.tracked_word for tab_tracked_word in self.tab_tracked_words.all()]

class TabWebsite(models.Model):
    tab = models.ForeignKey(Tab, on_delete=models.CASCADE, related_name="tab_websites")
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="website_tabs")
    
    class Meta:
      verbose_name = "Сайт во вкладке"
      verbose_name_plural = "Сайты во вкладке"
      
    def __str__(self):
        return self.website.name

class TabCountry(models.Model):
    tab = models.ForeignKey(Tab, on_delete=models.CASCADE, related_name="tab_countries")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="country_tabs")
    
    class Meta:
      verbose_name = "Страна во вкладке"
      verbose_name_plural = "Страны во вкладке"
    
    def __str__(self):
        return self.country.name

class TabTrackedWord(models.Model):
    tab = models.ForeignKey(Tab, on_delete=models.CASCADE, related_name="tab_tracked_words")
    tracked_word = models.ForeignKey(TrackedWord, on_delete=models.CASCADE, related_name="tracked_word_tabs")
    
    class Meta:
      verbose_name = "Отслеживаемое слово во вкладке"
      verbose_name_plural = "Отслеживаемые слова во вкладке"
    
    def __str__(self):
        return self.tracked_word.keyword


class Task(models.Model):
    class TaskStatus(models.TextChoices):
        PENDING = 'pending', 'Отложено'
        IN_PROGRESS = 'in_progress', 'В Процессе'
        COMPLETED = 'completed', 'Отработано'

    class Priority(models.IntegerChoices):
        LOW = 1, 'Низкий'
        MEDIUM = 2, 'Средний'
        HIGH = 3, 'Высокий'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', verbose_name='Пользователь')
    article = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Статья')
    status = models.CharField(
        max_length=20, 
        choices=TaskStatus.choices, 
        default=TaskStatus.PENDING, 
        verbose_name='Статус'
    )
    priority = models.IntegerField(
        choices=Priority.choices, 
        default=Priority.MEDIUM, 
        verbose_name='Приоритет')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return f"{self.user.username} - {self.article.title} - {self.get_status_display()} - {self.get_priority_display()}"

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments', verbose_name='Задача')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f"{self.user.username} - {self.task} - {self.created_at}"
    


from django.conf import settings

class UserDevice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    device_info = models.CharField(max_length=256, null=True, blank=True)
    session_key = models.CharField(max_length=256, null=True, blank=True)   
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} - {self.device_info}"
    
    

# @receiver(user_logged_in)
# def on_user_logged_in(sender, request, user, **kwargs):
#     device_info = request.session.session_key

#     # Удаление старой сессии, если есть 3 активные сессии
#     user_sessions = UserDevice.objects.filter(user=user)
#     if user_sessions.count() >= 3:
#         oldest_session = user_sessions.first()
#         UserDevice.objects.filter(device_info=oldest_session.device_info).delete()
#         oldest_session.delete()
#         Session.objects.filter(session_key=oldest_session.device_info).delete()

#     # Добавление новой сессии
#     UserDevice.objects.create(user=user, device_info=device_info)
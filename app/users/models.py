from django.db import models
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from main.models import Country, TrackedWord, Website

# Create your models here.
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


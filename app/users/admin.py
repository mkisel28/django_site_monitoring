from django.contrib import admin

from .models import Tab, TabCountry, TabTrackedWord, TabWebsite

# Register your models here.
@admin.register(Tab)
class TabAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name', 'user__username')
    list_filter = ('user',)
    raw_id_fields = ('user',)

# Регистрация модели TabWebsite
@admin.register(TabWebsite)
class TabWebsiteAdmin(admin.ModelAdmin):
    list_display = ('tab', 'website')
    search_fields = ('tab__name', 'website__name')
    list_filter = ('tab',)
    raw_id_fields = ('tab', 'website')

# Регистрация модели TabCountry
@admin.register(TabCountry)
class TabCountryAdmin(admin.ModelAdmin):
    list_display = ('tab', 'country')
    search_fields = ('tab__name', 'country__name')
    list_filter = ('tab',)
    raw_id_fields = ('tab', 'country')

# Регистрация модели TabTrackedWord
@admin.register(TabTrackedWord)
class TabTrackedWordAdmin(admin.ModelAdmin):
    list_display = ('tab', 'tracked_word')
    search_fields = ('tab__name', 'tracked_word__keyword')
    list_filter = ('tab',)
    raw_id_fields = ('tab', 'tracked_word')
    
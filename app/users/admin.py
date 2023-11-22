from django.contrib import admin

from .models import Tab, TabCountry, TabTrackedWord, TabWebsite, Task, Comment, UserDevice


# Register your models here.
@admin.register(Tab)
class TabAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'get_countries', 'get_websites', 'get_tracked_words')
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

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'status', 'priority', 'created_at', 'updated_at')
    list_filter = ('status', 'priority', 'created_at', 'user')
    search_fields = ('article__title', 'user__username')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user', 'article')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'text', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('task__article__title', 'user__username', 'text')
    date_hierarchy = 'created_at'
    
    
@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'device_info')
    list_filter = ('user',)
    search_fields = ('user__username', 'device_info')
    raw_id_fields = ('user',)
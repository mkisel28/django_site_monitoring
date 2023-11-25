from django.contrib import admin


from .models import (Website, 
                     Article, Country,
                     IgnoredURL, Word,
                     Configuration, 
                     TrackedWord, 
                     TrackedWordMention, 
                     UserProfile)

@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_url', 'last_scraped', 'country', 'id', 'user']
    search_fields = ['name']
    list_filter = ['last_scraped', 'country', "user"]



@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'website', "category", "eng_title",
                    'published_at', 'created_at', 'url', 'display_country']
    search_fields = ['title', 'title_translate', 'website__name']
    list_filter = ['created_at', 'website', 'website__country']
    
    actions = ['clear_eng_title', 'clear_category', 'clear_all_categories', 'clear_all_eng_titles']
    
    def clear_eng_title(self, request, queryset):
        queryset.update(eng_title=None)
    clear_eng_title.short_description = "Очистить английские названия"

    def clear_category(self, request, queryset):
        queryset.update(category=None)
    clear_category.short_description = "Очистить категории"

    def display_country(self, obj):
        return obj.website.country.name if obj.website.country else '-'
    display_country.short_description = 'Страна'
    
    def clear_all_categories(self, request, queryset):
        Article.objects.all().update(category=None)
    clear_all_categories.short_description = "Очистить категории всех статей"
    
    def clear_all_eng_titles(self, request, queryset):
        Article.objects.all().update(eng_title=None)
    clear_all_eng_titles.short_description = "Очистить английские названия всех статей"
    
    



@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']
    list_filter = ['name', 'code']




class IgnoredURLAdmin(admin.ModelAdmin):
    list_display = ['base_url']


admin.site.register(IgnoredURL, IgnoredURLAdmin)

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'frequency',
                    'timestamp']
    list_filter = ['frequency',
                   'timestamp']



@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name',
                    'black_list_tags',
                    'black_list_words',
                    'hours',
                    'top_words_count'
                    ]



@admin.register(TrackedWord)
class TrackedWordAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'keyword'
                    ]
    list_filter = ['user']



@admin.register(TrackedWordMention)
class TrackedWordMentionAdmin(admin.ModelAdmin):
    list_display = ['word', 'article','url' ]
    list_filter = ['word__user', 'word']


    def url(self, obj):
        return obj.article.url if obj.article.url else '-'
    url.short_description = 'URL'



@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'telegram_chat_id', 'telegram_notifications']
    list_filter = ['user']



    
    

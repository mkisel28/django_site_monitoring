from django.contrib import admin

 
from .models import Website, Article, Country, IgnoredURL, Word, Configuration, TrackedWord, TrackedWordMention, UserProfile

class WebsiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_url', 'last_scraped', 'country', 'id']
    search_fields = ['name']
    list_filter = ['last_scraped', 'country']

admin.site.register(Website, WebsiteAdmin)

class ArticleAdmin(admin.ModelAdmin):
    list_display = ['id','title', 'website', 'published_at', 'url', 'display_country']
    search_fields = ['title', 'title_translate', 'website__name']
    list_filter = ['published_at', 'website', 'website__country']

    def display_country(self, obj):
        return obj.website.country.name if obj.website.country else '-'
    display_country.short_description = 'Страна'

admin.site.register(Article, ArticleAdmin)


class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']
    list_filter = ['name', 'code']

admin.site.register(Country, CountryAdmin)


class IgnoredURLAdmin(admin.ModelAdmin):
    list_display = ['base_url']


admin.site.register(IgnoredURL, IgnoredURLAdmin)


class WordAdmin(admin.ModelAdmin):
    list_display = ['id','text', 'frequency',
                    'timestamp']
    list_filter = ['frequency',
                    'timestamp']

admin.site.register(Word, WordAdmin)


class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 
                    'black_list_tags',
                    'black_list_words',
                    'hours',
                    'top_words_count'
                    ]


admin.site.register(Configuration, ConfigurationAdmin)




class TrackedWordAdmin(admin.ModelAdmin):
    list_display = ['user', 
                    'keyword'
                    ]
    list_filter = ['user']

admin.site.register(TrackedWord, TrackedWordAdmin)





class TrackedWordMentionAdmin(admin.ModelAdmin):
    list_display = ['display_word', 'url']
    list_filter = ['word__user', 'word']
    
    def display_word(self, obj):
        return obj.word.keyword if obj.word.keyword else '-'
    display_word.short_description = 'Слово'
    def url(self, obj):
        return obj.article.url if obj.article.url else '-'
    url.short_description = 'URL'

admin.site.register(TrackedWordMention, TrackedWordMentionAdmin)




class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'telegram_chat_id', 'telegram_notifications']
    list_filter = ['user']

admin.site.register(UserProfile, UserProfileAdmin)
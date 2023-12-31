

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from main.models import TrackedWord, Website, Country


User = get_user_model()

class RegistrationForm(UserCreationForm):


    class Meta:
        model = User
        fields = ("username", "password1", "password2")

class TrackedWordForm(forms.ModelForm):
    class Meta:
        model = TrackedWord
        fields = ['keyword']

    def __init__(self, *args, **kwargs):
        super(TrackedWordForm, self).__init__(*args, **kwargs)
        self.fields['keyword'].widget.attrs['placeholder'] = 'Введите слово'


# class WebsiteURLForm(forms.Form):
#     url = forms.URLField(label="URL сайта")

class SitemapChoiceForm(forms.Form):
    sitemap = forms.ChoiceField(label="Выберите SITEMAP", choices=[])
    
    def __init__(self, *args, sitemaps=None, **kwargs):
        super().__init__(*args, **kwargs)
        if sitemaps:

            self.fields['sitemap'].choices = sitemaps

class AddWebsiteForm(forms.ModelForm):
    # Поле для выбора sitemap из списка
    
    # Поле для выбора страны из списка всех стран
    country = forms.ModelChoiceField(queryset=Country.objects.all(), required=False, label="Страна")
    
    class Meta:
        model = Website
        fields = ['name', 'base_url', 'language', 'country', 'sitemap_url']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Название сайта'}),
            'base_url': forms.URLInput(attrs={'readonly': 'readonly'}),  # только для чтения
            'language': forms.TextInput(attrs={'placeholder': 'Язык (например, ru)'}),
        }



class URLInputForm(forms.Form):
    url = forms.URLField(label='Введите URL сайта', widget=forms.URLInput(attrs={'placeholder': 'https://example.com'}))
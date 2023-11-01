from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name = 'users'


urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='registration/login.html',next_page='websites/', redirect_authenticated_user = True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/login_out.html'), name='logout'),
    path('register/', views.register, name='register'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),






    path('manage/', views.manage_tracked_words, name='manage_tracked_words'),
    path('add_word_api/', views.add_word_api, name='add_word_api'),
    path('delete_word_api/<int:word_id>/', views.delete_word_api, name='delete_word_api'),



    path('toggle_telegram_notifications/', views.toggle_telegram_notifications, name='toggle_telegram_notifications'),

]
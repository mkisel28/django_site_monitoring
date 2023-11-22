from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name = 'users'


urlpatterns = [
    path('', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/login_out.html'), name='logout'),
    path('register/', views.register, name='register'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),


    path("fetch_sitemaps/", views.fetch_sitemaps, name="fetch_sitemaps"),
    path("fetch_website_details/", views.fetch_website_details, name="fetch_website_details"),
    path('save_website/', views.save_website, name='save_website'),

    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('dashboard/settings/', views.dashboard_settings, name='dashboard_settings'),
    path('dashboard/trackword/', views.dashboard_trackword, name='dashboard_trackword'),
    path('dashboard/collection/', views.dashboard_collection, name='dashboard_collection'),
    path('dashboard/sites/', views.dashboard_sites, name='dashboard_sites'),
    
    path('add_word_api/', views.add_word_api, name='add_word_api'),
    path('delete_word_api/<int:word_id>/', views.delete_word_api, name='delete_word_api'),

    path('toggle_telegram_notifications/', views.toggle_telegram_notifications, name='toggle_telegram_notifications'),


    path('api/tabs/create/', views.api_manage_tab, name='api-create-tab'),
    
    path('api/update-tab/', views.update_tab, name='update_tab'),
    
    path('api/tasks/create/', views.api_task_create, name='api_task_create'),
    path('api/tasks/update/' , views.api_task_update, name='api_task_update'),
    
    path('api/tasks/info/' , views.api_get_all_tasks, name='api_get_all_tasks'),
    path('api/tasks/info/<int:article_id>/', views.api_task_info, name='api_task_info'),
    
    
    
    path('api/finger/', views.finger, name='api_finger'),
]
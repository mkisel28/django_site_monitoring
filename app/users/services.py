from django.shortcuts import get_object_or_404
from main.models import Article
from .models import Task

class TaskService:
    @staticmethod
    def create_task(user, article_id, status, priority):
        article = get_object_or_404(Article, id=article_id)
        task = Task.objects.create(
            user=user,
            article=article,
            status=status,
            priority=priority
        )
        return task

    @staticmethod
    def update_task(article_id, user, status=None, priority=None):
        task = get_object_or_404(Task, article_id=article_id, user=user)
        if status:
            task.status = status
        if priority:
            task.priority = priority
        task.save()
        return task

    @staticmethod
    def get_task(article_id, user):
        return get_object_or_404(Task, article_id=article_id, user=user)

    @staticmethod
    def get_all_tasks(user, status_filter=None, priority_filter=None):
        tasks = Task.objects.filter(user=user)
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)
        return tasks
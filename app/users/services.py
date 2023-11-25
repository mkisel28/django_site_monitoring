from typing import List, Optional
from django.shortcuts import get_object_or_404
from main.models import Article
from .models import Task
from django.contrib.auth.models import User


class TaskService:
    """
    Класс  для управления задачами, связанными со статьями.

    Methods:
        - `create_task`: Создает новую задачу.
        - `update_task`: Обновляет существующую задачу.
        - `get_task`: Получает конкретную задачу.
        - `get_all_tasks`: Получает все задачи для данного пользователя с возможной фильтрацией.
    """

    @staticmethod
    def create_task(user: User, article_id: int, status: str, priority: int) -> Task:
        """
        Создает новую задачу, связанную со статьей.

        Args:
            - `user` (User): Пользователь, которому назначена задача.
            - `article_id` (int): ID статьи, связанной с задачей.
            - `status` (str): Начальный статус задачи.
            - `priority` (int): Приоритет задачи.

        Returns:
            `Task`: Созданный объект задачи.
        """
        article = get_object_or_404(Article, id=article_id)
        task = Task.objects.create(
            user=user, article=article, status=status, priority=priority
        )
        return task

    @staticmethod
    def update_task(
        article_id: int,
        user: User,
        status: Optional[str] = None,
        priority: Optional[int] = None,
    ) -> Task:
        """
        Обновляет статус и/или приоритет существующей задачи.

        Args:
           - `article_id` (int): ID статьи, связанной с задачей.
           - `user` (User): Пользователь, которому назначена задача.
           - `status` (str, optional): Новый статус задачи. По умолчанию None.
           - `priority` (int, optional): Новый приоритет задачи. По умолчанию None.

        Returns:
            `Task`: Обновленный объект задачи.
        """
        task = get_object_or_404(Task, article_id=article_id, user=user)
        if status:
            task.status = status
        if priority:
            task.priority = priority
        task.save()
        return task

    @staticmethod
    def get_task(article_id: int, user: User) -> Task:
        """
        Получает задачу на основе ID статьи и пользователя.

        Args:
            - `article_id` (int): ID статьи, связанной с задачей.
            - `user` (User): Пользователь, которому назначена задача.

        Returns:
            `Task`: Запрашиваемый объект задачи.
        """
        return get_object_or_404(Task, article_id=article_id, user=user)

    @staticmethod
    def get_all_tasks(
        user: User,
        status_filter: Optional[str] = None,
        priority_filter: Optional[int] = None,
    ) -> List[Task]:
        """
        Получает все задачи для данного пользователя с возможной фильтрацией по статусу и приоритету.

        Args:
            - `user` (User): Пользователь, чьи задачи необходимо получить.
            - `status_filter` (str, optional): Статус для фильтрации задач. По умолчанию `None`.
            - `priority_filter` (int, optional): Уровень приоритета для фильтрации задач. По умолчанию `None`.

        Returns:
            `List[Task]`: Список объектов задач, соответствующих критериям.
        """
        tasks = Task.objects.filter(user=user)
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)
        return tasks

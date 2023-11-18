from django.utils import timezone
from django.contrib.auth.models import User

class UpdateLastLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Обновление даты последнего входа
        if request.user.is_authenticated:
            User.objects.filter(id=request.user.id).update(last_login=timezone.now())

        return response
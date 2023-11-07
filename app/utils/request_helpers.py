from typing import List
from django.http import HttpRequest


def get_int_list_from_request(request: HttpRequest, param_name: str) -> List[int]:
    """Extracts list of integers from the request's GET parameter."""
    return [int(x) for x in request.GET.get(param_name).split(",") if x] if request.GET.get(param_name) else []



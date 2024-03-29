from django.core.paginator import Paginator

from django.conf import settings


def get_page(request, posts):
    paginator = Paginator(posts, settings.PAGE_AMOUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj

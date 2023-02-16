"""Custom pagination."""

from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class PageNumberLimitPagination(PageNumberPagination):
    """Custom pagination: page number, item limit."""

    page_size_query_param = "limit"
    page_size = settings.PAGE_SIZE
    max_page_size = settings.MAX_PAGE_SIZE


class LimitPagination(PageNumberPagination):
    """Custom pagination: item limit."""

    page_size = settings.DEFAULT_LIMIT
    page_size_query_param = "recipes_limit"
    max_page_size = settings.MAX_LIMIT

    def get_paginated_response(self, data):
        return data

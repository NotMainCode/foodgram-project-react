"""Custom pagination."""

from django.conf import settings
from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination,
)


class PageNumberLimitPagination(PageNumberPagination):
    """Custom pagination: page number, item limit."""

    page_size_query_param = "limit"
    page_size = settings.PAGE_SIZE
    max_page_size = settings.MAX_PAGE_SIZE


class LimitPagination(LimitOffsetPagination):
    """"""

    limit_query_param = "recipes_limit"
    offset_query_param = None
    default_limit = settings.DEFAULT_LIMIT
    max_limit = settings.MAX_LIMIT

    def get_paginated_response(self, data):
        return data

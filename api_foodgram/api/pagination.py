"""Custom pagination."""

from rest_framework.pagination import PageNumberPagination


class PageNumberLimitPagination(PageNumberPagination):
    """Custom pagination: page number, item limit."""

    page_size_query_param = "limit"
    page_size = 6
    max_page_size = 24

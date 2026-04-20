from rest_framework.pagination import PageNumberPagination


class LargeResultsSetPagination(PageNumberPagination):
    """Custom pagination with configurable page size."""

    page_size = 6
    page_size_query_param = 'page_size'

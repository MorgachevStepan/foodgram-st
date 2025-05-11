from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    """
    Кастомный пагинатор, использующий query-параметр 'limit' для размера страницы.
    """
    page_size_query_param = 'limit'
    max_page_size = 100
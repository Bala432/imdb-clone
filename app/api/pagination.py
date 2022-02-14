from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination

class ReviewListPagination(PageNumberPagination):
    page_size = 5
    # page_query_param = 'sequence'
    page_size_query_param = 'size'
    max_page_size = 10
    # last_page_strings = 'last'
    
class ReviewListLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 5
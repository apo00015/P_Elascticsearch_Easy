from p_elasticsearch_easy.exceptions.custom_exceptions import CustomException


class ElasticsearchException(CustomException):
    def __init__(self, message=None):
        CustomException.__init__(self, message)

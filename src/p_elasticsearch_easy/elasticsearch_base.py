from abc import ABC, abstractmethod


class ElasticsearchBase(ABC):
    def __init__(self, url_connection):
        self.__elastic_settings = None
        self.__elasticsearch_client = None

        self.elastic_settings = url_connection

    @property
    def elastic_settings(self):
        return self.__elastic_settings

    @elastic_settings.setter
    def elastic_settings(self, value):
        if not isinstance(value, str) or value is None:
            raise ValueError("La configuración de conexión debe ser un string")
        self.__elastic_settings = value

    @abstractmethod
    def connect(self): ...

    @abstractmethod
    def get_document_by_id(self, id: str, index: str): ...

    @abstractmethod
    def close(self): ...

    @abstractmethod
    def count(self, index: str, body: dict): ...

    @abstractmethod
    def msearch(self): ...

    @abstractmethod
    def search_all(self, data, index): ...

    @abstractmethod
    def index(self, document, index): ...

    @abstractmethod
    def search(self, data, index): ...

    @abstractmethod
    def update(self): ...

    @abstractmethod
    def bulk(self, actions: list): ...

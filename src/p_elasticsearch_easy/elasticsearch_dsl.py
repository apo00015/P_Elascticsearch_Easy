import logging

from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk
from elasticsearch_dsl import Document, MultiSearch, Search, connections

from p_elasticsearch_easy.constants import MAX_SIZE, TIMEOUT
from p_elasticsearch_easy.elasticsearch_base import ElasticsearchBase
from p_elasticsearch_easy.exceptions.elasticsearch_exception import ElasticsearchException


class ElasticsearchDSL(ElasticsearchBase):
    """
    A concrete implementation of ElasticsearchBase that provides native access to Elasticsearch operations.
    """

    def __init__(self, url_connection, name_connection: str = "Default") -> None:
        """
        Initializes the Elasticsearch connection handler.

        :param url_connection: Optional URL or configuration used to connect to the Elasticsearch instance.
                               If not provided, the connection should be configured by the base class or defaults.
        :type url_connection: Any, optional
        :param name_connection: A custom name or label to identify the connection instance.
                                Defaults to "Default".
        :type name_connection: str
        """
        super().__init__(url_connection)
        self.__name_connection = None
        self.name_connection = name_connection

    @property
    def name_connection(self):
        return self.__name_connection

    @name_connection.setter
    def name_connection(self, value):
        if value is None or not isinstance(value, str):
            raise ValueError("name_connection must be a non-null string.")
        self.__name_connection = value

    def connect(self, timeout_elastic: int = TIMEOUT.ELASTIC):
        """
        Establishes a connection to Elasticsearch using the defined configuration.

        :param timeout_elastic: Timeout value for the connection.
        :raises ElasticsearchException: If the connection cannot be established.
        """
        try:
            new_elastic = Elasticsearch(self.elastic_settings, timeout=timeout_elastic, max_retries=6, retry_on_timeout=True)

            connections.add_connection(self.name_connection, new_elastic)

            self.__elasticsearch_client = connections.get_connection(self.name_connection)
        except:
            raise ElasticsearchException(f"Error to connect with node {self.elastic_settings}")

    def get_document_by_id(self, id: str, index: str) -> Document:
        """
        Retrieves a document from Elasticsearch by its ID using elasticsearch_dsl.

        :param id: ID of the document to retrieve.
        :type id: str
        :param index: Name of the index containing the document.
        :type index: str
        :return: The retrieved document as a Document object.
        :rtype: elasticsearch_dsl.Document
        :raises ElasticsearchException: If an error occurs during retrieval.
        """
        try:
            return Document.get(id=id, index=index, using=self.__elasticsearch_client)
        except Exception as e:
            raise ElasticsearchException(f"Error retrieving document with ID '{id}' from index '{index}': {e}")

    def update(self, document: Document):
        """
        Saves changes to an existing Elasticsearch document using elasticsearch_dsl.

        :param document: An instance of a Document (elasticsearch_dsl.Document) to be updated.
        :type document: Document
        :return: The updated document as a dictionary.
        :rtype: dict
        :raises ElasticsearchException: If an error occurs while saving the document.
        """
        try:
            document.save(refresh="wait_for")
            return document.to_dict()
        except Exception as e:
            raise ElasticsearchException(f"Error updating document: {e}")

    def index(self, document: Document, index: str):
        """
        Indexes a new document into the specified Elasticsearch index using elasticsearch_dsl.

        :param document: An instance of a Document (elasticsearch_dsl.Document) to be indexed.
        :type document: Document
        :param index: The name of the Elasticsearch index where the document will be stored.
        :type index: str
        :return: Boolean indicating whether the operation was successful.
        :rtype: bool
        :raises ElasticsearchException: If an error occurs while indexing the document.
        """
        try:
            return document.save(using=self.__elasticsearch_client, index=index)
        except Exception:
            raise ElasticsearchException(f"Error to insert new data in {index}")

    def bulk(self, actions: list):
        """
        Executes a bulk operation using elasticsearch_dsl's parallel_bulk to process multiple actions efficiently.

        This method performs the bulk indexing or updating of documents in parallel. Errors are logged,
        but the process continues for the rest of the actions. The operation uses `refresh="wait_for"` to make
        the changes searchable after completion.

        :param actions: A list of action dictionaries formatted according to the Elasticsearch bulk API.
                        Each action can include operations such as index, update, or delete.
        :type actions: list
        :raises ElasticsearchException: If a critical error occurs during the bulk operation.
        """
        try:
            for success_errors, failed_errors in parallel_bulk(
                self.__elasticsearch_client, actions=actions, raise_on_error=False, refresh="wait_for"
            ):
                if not success_errors:
                    logging.error(failed_errors["index"]["error"]["reason"])
        except:
            raise ElasticsearchException("Error in bulk")

    def search(self, data, index, source, size=1):
        """
        Executes a search query using elasticsearch_dsl on the specified index with custom query, source filtering, and size.

        :param data: The query to be executed. This should be a Query object or any valid query input for elasticsearch_dsl.
        :type data: Any
        :param index: The name of the Elasticsearch index where the search will be performed.
        :type index: str
        :param source: A list of fields to include in the response (_source filtering).
        :type source: list or str
        :param size: The maximum number of documents to return. Defaults to 1.
        :type size: int, optional
        :return: The search response containing matched documents and metadata.
        :rtype: elasticsearch_dsl.response.Response
        :raises ElasticsearchException: If an error occurs during the search operation.
        """
        try:
            search = Search(using=self.__elasticsearch_client, index=index).query(data).source(source).extra(size=size)

            response = search.execute()

            return response
        except:
            raise ElasticsearchException(f"Error searching data {data} in {index}")

    def search_all(self, data, index: str, source: list, only_source: bool = True) -> list:
        """
        Executes a full search using elasticsearch_dsl's scan method to retrieve all matching documents from the specified index.

        This method is optimized for large result sets and uses the scroll API under the hood. It allows filtering
        the response to return only the `_source` content or the full Document objects.

        :param data: The query to execute. Should be a valid elasticsearch_dsl Query object or equivalent.
        :type data: Any
        :param index: The name of the Elasticsearch index to search.
        :type index: str
        :param source: List of fields to include from the document `_source`.
        :type source: list
        :param only_source: Whether to return only the document source as a dictionary (`True`)
                            or the full Document objects (`False`). Defaults to `True`.
        :type only_source: bool, optional
        :return: A list of matching documents. Each item is either a dictionary or a Document object depending on `only_source`.
        :rtype: list
        :raises ElasticsearchException: If an error occurs during the search operation.
        """
        try:
            s = Search(using=self.__elasticsearch_client, index=index).source(source).query(data).extra(size=MAX_SIZE)

            documents = [item.to_dict() if only_source else item for item in s.scan()]

            return documents
        except:
            raise ElasticsearchException(f"Error searching data {data} in {index}")

    def msearch(self, searches: list, index: str, source: list) -> list:
        """
        Executes multiple search queries in batches using Elasticsearch's MultiSearch API via elasticsearch_dsl.

        This method takes a list of query objects, splits them into batches of size `MAX_SIZE`, and performs
        a multi-search (`msearch`) operation for each batch. Each query retrieves one result by default (`size=1`).
        It allows filtering specific `_source` fields in the response.

        :param searches: A list of query objects to be executed. Each item should be compatible with elasticsearch_dsl.
        :type searches: list
        :param index: The name of the Elasticsearch index where the searches will be performed.
        :type index: str
        :param source: List of fields to include in the `_source` of each returned document.
        :type source: list
        :return: A list of search results, each corresponding to one of the input queries.
        :rtype: list
        :raises ElasticsearchException: If an error occurs during the multi-search operation.
        """
        try:
            results = []
            for batch_start in range(0, len(searches), MAX_SIZE):
                batch = searches[batch_start : batch_start + MAX_SIZE]
                ms = MultiSearch(using=self.__elasticsearch_client, index=index)
                for item in batch:
                    s = Search().query(item).source(source).extra(size=1)
                    ms = ms.add(search=s)

                results.extend(ms.execute())

            return results
        except Exception as e:
            raise ElasticsearchException(f"Error performing multi search operations: {e}")

    def count(self, index: str, body: dict) -> int:
        """
        Executes a count query using elasticsearch_dsl to determine the number of documents
        that match the specified query in the given index.

        :param index: The name of the Elasticsearch index where the count operation will be performed.
        :type index: str
        :param body: A dictionary representing the query to be applied for counting documents.
                     Should be a valid Elasticsearch DSL query.
        :type body: dict
        :return: The number of documents that match the query.
        :rtype: int
        :raises ElasticsearchException: If an error occurs during the count operation.
        """
        try:
            search = Search(using=self.__elasticsearch_client, index=index).query(body)
            return search.count()
        except:
            raise ElasticsearchException(f"Error count data {body} in {index}")

    def close(self):
        """
        Closes the current connection to the Elasticsearch client.

        This method should be called when the client is no longer needed
        to ensure that resources such as open sockets and connections are properly released.

        :raises ElasticsearchException: If an error occurs while attempting to close the connection.
        """
        try:
            self.__elasticsearch_client.close()
        except:
            raise ElasticsearchException("Error closing connection")

import json

from elasticsearch import Elasticsearch, helpers

from p_elasticsearch_easy.constants.constants import MAX_SIZE, TIMEOUT
from p_elasticsearch_easy.elasticsearch_base import ElasticsearchBase
from p_elasticsearch_easy.exceptions.elasticsearch_exception import ElasticsearchException


class ElasticsearchNative(ElasticsearchBase):
    """
    A concrete implementation of ElasticsearchBase that provides native access to Elasticsearch operations.
    """

    def __init__(self, url_connection: str) -> None:
        """
        Initializes the ElasticsearchNative class with a connection URL.

        :param url_connection: URL of the Elasticsearch node or cluster.
        """
        super().__init__(url_connection)

    def connect(self, timeout_elastic: int = TIMEOUT.ELASTIC) -> None:
        """
        Establishes a connection to Elasticsearch using the defined configuration.

        :param timeout_elastic: Timeout value for the connection.
        :raises ElasticsearchException: If the connection cannot be established.
        """
        try:
            self.__elasticsearch_client = Elasticsearch(self.elastic_settings, timeout=timeout_elastic, max_retries=6, retry_on_timeout=True)
        except:
            raise ElasticsearchException(f"Error to connect with node {self.elastic_settings}")

    def get_document_by_id(self, id: str, index: str):
        """
        Retrieves a document from Elasticsearch by its ID.

        :param id: ID of the document to retrieve.
        :type id: str
        :param index: Name of the index where the document is located.
        :type index: str
        :return: The document retrieved from Elasticsearch.
        :rtype: dict
        :raises ElasticsearchException: If an error occurs while retrieving the document.
        """
        try:
            return self.__elasticsearch_client.get(index=index, id=id)
        except:
            raise ElasticsearchException(f"Error searching id in {index}")

    def delete_by_query(self, information, index):
        """
        Deletes documents from the specified Elasticsearch index that match the given query.

        The query is serialized to JSON before being sent to Elasticsearch. If the query contains custom
        objects, they are automatically converted using their `__dict__` attribute.

        :param information: A query that defines which documents to delete.
                            Should be a dictionary or an object serializable to JSON.
        :type information: dict or Any serializable
        :param index: The name of the Elasticsearch index where the documents will be deleted.
        :type index: str
        :return: A dictionary with the result of the delete_by_query operation, including metadata such as
                 number of documents deleted.
        :rtype: dict
        :raises ElasticsearchException: If an error occurs during the delete_by_query operation.
        """
        try:
            information = json.dumps(information, default=lambda y: y.__dict__)
            return self.__elasticsearch_client.delete_by_query(index=index, body=information)
        except:
            raise ElasticsearchException(f"Error to delete_by_query in {index}")

    def update(self, document: dict, id: str, index: str):
        """
        Updates a document in Elasticsearch with new information.

        :param information: Dictionary containing the data to update in the document.
        :type information: dict
        :param id: ID of the document to be updated.
        :type id: str
        :param index: Name of the index where the document is located.
        :type index: str
        :return: Response from the Elasticsearch client after the update operation.
        :rtype: dict
        :raises ElasticsearchException: If an error occurs during the document update.
        """
        try:
            return self.__elasticsearch_client.update(index=index, id=id, doc=document, refresh="wait_for")
        except:
            raise ElasticsearchException(f"Error to update new data in {index}")

    def update_by_query(self, body: dict, index: str, wait_for="true"):
        """
        Executes an `update_by_query` operation in Elasticsearch to update multiple documents
        that match the specified query.

        :param body: The query body containing the search criteria and the update script (painless).
        :type body: dict
        :param index: Name of the index where the update will be performed.
        :type index: str
        :param wait_for: Defines whether to wait for the index to be refreshed before continuing.
                         This parameter is passed to the `refresh` field of the operation.
        :type wait_for: str
        :return: Elasticsearch response with details of the operation (`updated`, `failures`, etc.).
        :rtype: dict
        :raises ElasticsearchException: If an error occurs during the update operation.
        """
        try:
            return self.__elasticsearch_client.update_by_query(index=index, body=body, refresh=wait_for)
        except:
            raise ElasticsearchException(f"Error to update data with painless script in {index}")

    def index(self, document: dict, index: str, id: str = None):
        """
        Indexes a new document into the specified Elasticsearch index.

        The provided dictionary is serialized into JSON before being sent. If the dictionary contains
        objects, they are converted using their `__dict__` attribute.

        :param document: A dictionary representing the document to be indexed.
                        Objects within the dictionary will be serialized automatically.
        :type document: dict
        :param index: The name of the Elasticsearch index where the document will be stored.
        :type index: str
        :param id: Optional ID to assign to the document. If not provided, Elasticsearch will generate one.
        :type id: str, optional
        :return: Response from Elasticsearch confirming the indexing operation.
        :rtype: dict
        :raises ElasticsearchException: If an error occurs while indexing the document.
        """
        try:
            document = json.dumps(document, default=lambda y: y.__dict__)
            if id:
                return self.__elasticsearch_client.index(index=index, id=id, body=document)
            else:
                return self.__elasticsearch_client.index(index=index, body=document)
        except Exception as e:
            raise ElasticsearchException(f"Error to insert new data in {index}: {e}")

    def bulk(self, actions: list):
        """
        Executes a bulk operation in Elasticsearch using the provided list of actions.

        This method allows multiple indexing, updating, or deleting operations to be performed
        in a single request, which improves performance for large-scale data processing.

        :param actions: A list of action dictionaries to be executed in bulk.
                        Each action should follow the Elasticsearch bulk API format.
        :type actions: list
        :return: A tuple containing the number of successful operations and a list of errors (if any).
        :rtype: tuple
        :raises ElasticsearchException: If an error occurs during the bulk operation.
        """
        try:
            return helpers.bulk(self.__elasticsearch_client, actions)
        except:
            raise ElasticsearchException("Error performing bulk operations")

    def bulk_without_helper(self, operations: list, wait_for: str = "false"):
        """
        Executes a bulk operation in Elasticsearch without using the high-level `helpers.bulk` utility.

        This method sends the raw list of bulk operations directly to the Elasticsearch client.
        It supports custom control over refresh behavior using the `refresh` parameter.

        :param operations: A list of raw bulk operations formatted according to the Elasticsearch Bulk API.
                           Each operation should be a line-delimited JSON action (e.g., index, update, delete).
        :type operations: list
        :param wait_for: Defines the refresh behavior after the bulk operation.
                         Accepts "true", "false", or "wait_for".
                         - "true": refresh immediately
                         - "false": no refresh (default)
                         - "wait_for": wait until the next refresh cycle
        :type wait_for: str
        :return: A dictionary containing the results of the bulk operation.
        :rtype: dict
        :raises ElasticsearchException: If an error occurs during the bulk operation.
        """
        try:
            return self.__elasticsearch_client.bulk(operations=operations, refresh=wait_for)
        except:
            raise ElasticsearchException("Error performing bulk operation")

    def search(self, body: dict, index: str):
        """
        Executes a search query on the specified Elasticsearch index using the provided DSL query body.

        :param body: A dictionary representing the Elasticsearch DSL query.
                     This can include match queries, filters, aggregations, etc.
        :type body: dict
        :param index: The name of the index (or indices) where the search will be performed.
        :type index: str
        :return: A dictionary containing the search results, including hits and metadata.
        :rtype: dict
        :raises ElasticsearchException: If an error occurs during the search operation.
        """
        try:
            return self.__elasticsearch_client.search(index=index, body=body)
        except:
            raise ElasticsearchException(f"Error searching data {body} in {index}")

    def search_all(self, body: dict, index: str):
        """
        Executes a full search using the Elasticsearch scroll API to retrieve all matching documents
        from the specified index based on the provided query.

        :param body: A dictionary representing the Elasticsearch query.
        :type body: dict
        :param index: The name of the index from which documents will be retrieved.
        :type index: str
        :return: A list containing all matching documents returned by the scroll operation.
        :rtype: list
        :raises ElasticsearchException: If an error occurs during the search or scroll operations.
        """
        try:
            result_final = []
            scroll_id = "1m"

            response = self.__elasticsearch_client.search(index=index, body=body, scroll=scroll_id, size=MAX_SIZE)
            result_final.extend(response["hits"]["hits"])

            while len(response["hits"]["hits"]) > 0:
                response = self.__elasticsearch_client.scroll(scroll_id=response["_scroll_id"], scroll=scroll_id)
                result_final.extend(response["hits"]["hits"])

            return result_final
        except:
            raise ElasticsearchException(f"Error searching data {body} in {index}")

    def msearch(self, searches: list):
        """
        Executes a batch of search queries using Elasticsearch's multi-search (msearch) API.

        :param searches: A list of search queries formatted as dictionaries, where each query follows
                        the expected Elasticsearch msearch structure (i.e., alternating header and body).
        :type searches: list
        :return: A list of responses from Elasticsearch, one for each search query.
        :rtype: list
        :raises ElasticsearchException: If an error occurs while executing the multi-search operations.
        """
        try:
            results = []
            from_index = 0
            total_searches = len(searches)
            while from_index < total_searches:
                results_msearch = self.__elasticsearch_client.msearch(searches=searches[from_index : from_index + MAX_SIZE])
                results.extend(results_msearch["responses"])

                from_index += MAX_SIZE

            return results
        except Exception as e:
            raise ElasticsearchException(f"Error performing multi search operations: {e}")

    def count(self, index: str, body: dict) -> int:
        """
        Executes a count query on the specified Elasticsearch index using the provided query body.

        This method returns the number of documents that match the given query without retrieving the documents themselves.

        :param index: The name of the index to perform the count operation on.
        :type index: str
        :param body: A dictionary representing the Elasticsearch query in DSL format.
        :type body: dict
        :return: The number of documents that match the query.
        :rtype: int
        :raises ElasticsearchException: If an error occurs during the count operation.
        """
        try:
            resp_count = self.__elasticsearch_client.count(index=index, body=body)
            return resp_count["count"]
        except Exception as e:
            raise ElasticsearchException(f"Error performing count: {e}")

    def delete_by_id(self, index: str, id: str) -> dict:
        """
        Deletes a document from the specified Elasticsearch index by its ID.

        :param index: Name of the index where the document resides.
        :type index: str
        :param id: ID of the document to delete.
        :type id: str
        :return: The response from Elasticsearch confirming the deletion.
        :rtype: dict
        :raises ElasticsearchException: If an error occurs while deleting the document.
        """
        try:
            return self.__elasticsearch_client.delete(index=index, id=id)
        except Exception as e:
            raise ElasticsearchException(f"Error deleting document {id} from index {index}: {e}")

    def close(self) -> None:
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

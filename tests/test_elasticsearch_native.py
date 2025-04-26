import json
from unittest.mock import MagicMock, patch

import pytest

from p_elasticsearch_easy.exceptions.elasticsearch_exception import ElasticsearchException
from src.p_elasticsearch_easy.elasticsearch_native import ElasticsearchNative


class TestElaticSearchNative:
    @pytest.mark.parametrize(
        "url_connection",
        [("https:"), ("ANALITICA"), ("Default"), (""), ("http://localhost:9200")],
    )
    def test_initialization_success(self, url_connection):
        elastic_search_native = ElasticsearchNative(url_connection)
        assert elastic_search_native.elastic_settings == url_connection

    @patch("p_elasticsearch_easy.elasticsearch_native.Elasticsearch.__init__", side_effect=Exception("Connection failed"))
    def test_connect_failure(self, mock_elasticsearch):
        es = ElasticsearchNative("http://localhost:9200")
        with pytest.raises(ElasticsearchException, match="Error to connect with node"):
            es.connect()

    def test_get_document_by_id_success(self):
        es = ElasticsearchNative("http://localhost:9200")
        mock_client = MagicMock()
        mock_client.get.return_value = {"_id": "123", "_source": {"title": "doc test"}}
        es._ElasticsearchNative__elasticsearch_client = mock_client

        result = es.get_document_by_id("123", "my_index")

        assert result["_id"] == "123"
        assert result["_source"]["title"] == "doc test"

    def test_get_document_by_id_raises_elasticsearch_exception(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.get.side_effect = Exception("Documento no encontrado")
        es._ElasticsearchNative__elasticsearch_client = mock_client

        with pytest.raises(ElasticsearchException, match="Error searching id in my_index"):
            es.get_document_by_id("999", "my_index")

    def test_delete_by_query_success(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.delete_by_query.return_value = {"deleted": 3}
        es._ElasticsearchNative__elasticsearch_client = mock_client

        query = {"query": {"match": {"status": "deprecated"}}}

        response = es.delete_by_query(query, "my_index")

        mock_client.delete_by_query.assert_called_once()
        assert response["deleted"] == 3

    def test_delete_by_query_raises_elasticsearch_exception(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.delete_by_query.side_effect = Exception("Error en la operación")
        es._ElasticsearchNative__elasticsearch_client = mock_client

        query = {"query": {"match_all": {}}}

        with pytest.raises(ElasticsearchException, match="Error to delete_by_query in my_index"):
            es.delete_by_query(query, "my_index")

    def test_update_success(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.update.return_value = {"result": "updated"}
        es._ElasticsearchNative__elasticsearch_client = mock_client

        response = es.update(document={"name": "new"}, id="123", index="test_index")

        assert response["result"] == "updated"
        mock_client.update.assert_called_once_with(index="test_index", id="123", doc={"name": "new"}, refresh="wait_for")

    def test_update_raises_exception(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.update.side_effect = Exception("Simulated failure")
        es._ElasticsearchNative__elasticsearch_client = mock_client

        with pytest.raises(ElasticsearchException, match="Error to update new data in test_index"):
            es.update(document={"name": "error"}, id="456", index="test_index")

    def test_update_by_query_success(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.update_by_query.return_value = {"updated": 5, "failures": []}
        es._ElasticsearchNative__elasticsearch_client = mock_client

        query = {"script": {"source": "ctx._source.status = 'archived'", "lang": "painless"}, "query": {"match": {"status": "active"}}}

        response = es.update_by_query(body=query, index="my_index", wait_for="wait_for")

        assert response["updated"] == 5
        assert response["failures"] == []
        mock_client.update_by_query.assert_called_once_with(index="my_index", body=query, refresh="wait_for")

    def test_update_by_query_raises_exception(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.update_by_query.side_effect = Exception("Something went wrong")
        es._ElasticsearchNative__elasticsearch_client = mock_client

        with pytest.raises(ElasticsearchException, match="Error to update data with painless script in my_index"):
            es.update_by_query(body={}, index="my_index")

    def test_index_with_id(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.index.return_value = {"result": "created"}
        es._ElasticsearchNative__elasticsearch_client = mock_client

        doc = {"title": "Test Doc"}
        response = es.index(document=doc, index="my_index", id="doc123")

        expected_body = json.dumps(doc, default=lambda y: y.__dict__)
        mock_client.index.assert_called_once_with(index="my_index", id="doc123", body=expected_body)
        assert response["result"] == "created"

    def test_index_without_id(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.index.return_value = {"result": "created"}
        es._ElasticsearchNative__elasticsearch_client = mock_client

        doc = {"title": "Generated ID"}
        response = es.index(document=doc, index="my_index")

        expected_body = json.dumps(doc, default=lambda y: y.__dict__)
        mock_client.index.assert_called_once_with(index="my_index", body=expected_body)
        assert response["result"] == "created"

    def test_index_raises_exception(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.index.side_effect = Exception("Simulated error")
        es._ElasticsearchNative__elasticsearch_client = mock_client

        with pytest.raises(ElasticsearchException, match="Error to insert new data in my_index"):
            es.index(document={"title": "fail"}, index="my_index")

    @patch("src.p_elasticsearch_easy.elasticsearch_native.helpers.bulk")
    def test_bulk_success(self, mock_bulk):
        es = ElasticsearchNative("http://localhost:9200")

        mock_bulk.return_value = (2, [])  # 2 operaciones exitosas, 0 errores
        es._ElasticsearchNative__elasticsearch_client = MagicMock()

        actions = [
            {"_op_type": "index", "_index": "test", "_id": "1", "_source": {"title": "doc 1"}},
            {"_op_type": "index", "_index": "test", "_id": "2", "_source": {"title": "doc 2"}},
        ]

        result = es.bulk(actions)

        mock_bulk.assert_called_once_with(es._ElasticsearchNative__elasticsearch_client, actions)
        assert result == (2, [])

    @patch("src.p_elasticsearch_easy.elasticsearch_native.helpers.bulk")
    def test_bulk_raises_elasticsearch_exception(self, mock_bulk):
        es = ElasticsearchNative("http://localhost:9200")

        mock_bulk.side_effect = Exception("Simulated bulk failure")
        es._ElasticsearchNative__elasticsearch_client = MagicMock()

        actions = [{"_op_type": "index", "_index": "test", "_source": {"title": "doc"}}]

        with pytest.raises(ElasticsearchException, match="Error performing bulk operations"):
            es.bulk(actions)

    def test_bulk_without_helper_success(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.bulk.return_value = {"errors": False, "items": []}
        es._ElasticsearchNative__elasticsearch_client = mock_client

        operations = [{"index": {"_index": "test", "_id": "1"}}, {"title": "doc1"}, {"index": {"_index": "test", "_id": "2"}}, {"title": "doc2"}]

        response = es.bulk_without_helper(operations, wait_for="wait_for")

        mock_client.bulk.assert_called_once_with(operations=operations, refresh="wait_for")
        assert response["errors"] is False

    def test_search_success(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.search.return_value = {
            "hits": {"total": {"value": 2}, "hits": [{"_id": "1", "_source": {"title": "doc1"}}, {"_id": "2", "_source": {"title": "doc2"}}]}
        }
        es._ElasticsearchNative__elasticsearch_client = mock_client

        query = {"query": {"match_all": {}}}
        result = es.search(body=query, index="my_index")

        mock_client.search.assert_called_once_with(index="my_index", body=query)
        assert result["hits"]["total"]["value"] == 2

    def test_search_raises_exception(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.search.side_effect = Exception("Simulated search error")
        es._ElasticsearchNative__elasticsearch_client = mock_client

        with pytest.raises(ElasticsearchException, match="Error searching data"):
            es.search(body={"query": {"match": {"field": "value"}}}, index="my_index")

    def test_search_all_success(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()

        # Primera respuesta con hits
        first_response = {"_scroll_id": "abc123", "hits": {"hits": [{"_id": "1", "_source": {"title": "doc1"}}]}}

        # Segunda respuesta también con hits
        second_response = {"_scroll_id": "abc123", "hits": {"hits": [{"_id": "2", "_source": {"title": "doc2"}}]}}

        # Tercera respuesta vacía (fin del scroll)
        third_response = {"_scroll_id": "abc123", "hits": {"hits": []}}

        mock_client.search.return_value = first_response
        mock_client.scroll.side_effect = [second_response, third_response]

        es._ElasticsearchNative__elasticsearch_client = mock_client

        query = {"query": {"match_all": {}}}
        result = es.search_all(body=query, index="my_index")

        assert len(result) == 2
        assert result[0]["_id"] == "1"
        assert result[1]["_id"] == "2"

        mock_client.search.assert_called_once()
        assert mock_client.scroll.call_count == 2

    def test_search_all_raises_exception(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.search.side_effect = Exception("Simulated search failure")

        es._ElasticsearchNative__elasticsearch_client = mock_client

        with pytest.raises(ElasticsearchException, match="Error searching data"):
            es.search_all(body={"query": {"match_all": {}}}, index="my_index")

    def test_msearch_success(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.msearch.side_effect = [
            {"responses": [{"hits": {"hits": [{"_id": "1"}]}}, {"hits": {"hits": [{"_id": "2"}]}}]},
            {"responses": [{"hits": {"hits": [{"_id": "3"}]}}]},
        ]
        es._ElasticsearchNative__elasticsearch_client = mock_client

        searches = [
            {"index": "test"},
            {"query": {"match_all": {}}},
            {"index": "test"},
            {"query": {"match": {"title": "test"}}},
            {"index": "test"},
            {"query": {"match": {"title": "hello"}}},
        ]

        result = es.msearch(searches)

        assert len(result) == 2

        assert mock_client.msearch.call_count == 1

    def test_msearch_raises_exception(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.msearch.side_effect = Exception("Multi-search failed")
        es._ElasticsearchNative__elasticsearch_client = mock_client

        with pytest.raises(ElasticsearchException, match="Error performing multi search operations"):
            es.msearch([{"index": "test"}, {"query": {"match_all": {}}}])

    def test_count_success(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.count.return_value = {"count": 42}
        es._ElasticsearchNative__elasticsearch_client = mock_client

        query = {"query": {"match_all": {}}}
        result = es.count(index="my_index", body=query)

        mock_client.count.assert_called_once_with(index="my_index", body=query)
        assert result == 42

    def test_count_raises_exception(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.count.side_effect = Exception("Something went wrong")
        es._ElasticsearchNative__elasticsearch_client = mock_client

        with pytest.raises(ElasticsearchException, match="Error performing count"):
            es.count(index="my_index", body={"query": {"match": {"field": "value"}}})

    def test_delete_by_id_success(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.delete.return_value = {"_index": "my_index", "_id": "123", "result": "deleted"}
        es._ElasticsearchNative__elasticsearch_client = mock_client

        response = es.delete_by_id(index="my_index", id="123")

        mock_client.delete.assert_called_once_with(index="my_index", id="123")
        assert response["result"] == "deleted"

    def test_delete_by_id_raises_exception(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.delete.side_effect = Exception("Document not found")
        es._ElasticsearchNative__elasticsearch_client = mock_client

        with pytest.raises(ElasticsearchException, match="Error deleting document 123 from index my_index"):
            es.delete_by_id(index="my_index", id="123")

    def test_close_success(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        es._ElasticsearchNative__elasticsearch_client = mock_client

        es.close()

        mock_client.close.assert_called_once()

    def test_close_raises_exception(self):
        es = ElasticsearchNative("http://localhost:9200")

        mock_client = MagicMock()
        mock_client.close.side_effect = Exception("Connection close failed")
        es._ElasticsearchNative__elasticsearch_client = mock_client

        with pytest.raises(ElasticsearchException, match="Error closing connection"):
            es.close()

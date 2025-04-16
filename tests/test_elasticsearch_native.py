from src.p_elasticsearch_easy.elasticsearch_native import ElasticsearchNative


class TestElaticSearchNative:
    def test_initialization_success(self):
        elastic_search_native = ElasticsearchNative("")
        # assert elastic_search_native.__elastic_settings is None

    # def test_conecct_success(self):
    #     elastic_search_native = ElasticsearchNative("")

    #     assert elastic_search_native._elasticsearch_client is None
    #     elastic_search_native.connect()
    #     assert elastic_search_native._elasticsearch_client is not None

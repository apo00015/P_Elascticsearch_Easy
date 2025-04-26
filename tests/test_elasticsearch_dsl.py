import pytest

from src.p_elasticsearch_easy.elasticsearch_dsl import ElasticsearchDSL


class TestElaticSearchDSL:
    @pytest.mark.parametrize(
        "name_connection",
        [("PRO"), ("ANALITICA"), ("Default")],
    )
    def test_initialization_success(self, name_connection):
        elastic_search_dsl = ElasticsearchDSL("")
        assert elastic_search_dsl.name_connection == "Default"

        elastic_search_dsl_2 = ElasticsearchDSL("", name_connection)
        assert elastic_search_dsl_2.name_connection == name_connection

    @pytest.mark.parametrize(
        "name_connection",
        [(None), ({"name": "PRO"}), (100)],
    )
    def test_initialization_fail(self, name_connection):
        with pytest.raises(ValueError):
            ElasticsearchDSL("", name_connection)

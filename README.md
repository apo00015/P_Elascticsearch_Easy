# P_Elascticsearch_Easy

![Python Version](https://img.shields.io/badge/python-3.8%2B-red)
![License](https://img.shields.io/badge/license-GPLv3-green)

## Description

P_Elascticsearch_Easy is a Python utility that provides a simplified class for interacting with elasticsearch and elasticsearch_dsl.

## Features

- Create a connection with Elasticsearch
- Retrieve a document given an ID
- Perform a delete_by_query
- Update a document
- Perform an update_by_query
- Index a document
- Index a document given an ID
- Delete a document given an ID
- Perform a bulk operation using the helpers library
- Perform a native bulk operation without using the helpers library
- Perform searches in indices using queries
- Retrieve all documents matching a query
- Perform searches using msearch
- Perform searches using mget
- Get a count of documents matching a query

## Installation

You can install the package directly from PyPi using pip:

```bash
pip install p-elasticsearch-easy
```

## Usage

### Example of use ElasticsearchNative

```Python
from p_elasticsearch_easy import ElasticsearchNative

# Create de instancia of ElasticsearchNative
es_native: ElasticsearchNative = ElasticsearchNative("https://elastic.com:9243")

# Connect
es_native.connect()

# We execute the get_document_by_id
resp = es_native.search(id="id", index="name_index")

# We execute the delete_by_query
query = {"query":{"match_all":{}}}
es_native.delete_by_query(information=query, index="name_index")

# We execute de update
doc = {
    "field1": "value",
    "field_2": "value"
}
es_native.update(document=doc, id="id", index="name_index")

# We execute the update_by_query
query = {"query":{"match_all":{}}}
es_native.update_by_query(body=query, index="name_index", wait_for="true")

# We execute the index
doc = {
    "field1": "value",
    "field_2": "value"
}
es_native.index(document=doc, index="name_index")

# We execute the search
query = {
    "size": 10,
    "query": {"bool": {"must": [{"term": {"name_field": {"value": ""}}}]}},
}

resp = es_native.search(index="name_index", body=query)

# We execute the bulk
actions = [
    {
        "_op_type": "index",
        "_index": "mi_indice",
        "_source": {
            "title": "Documento 1",
            "contenido": "Este es el primer documento"
        }
    },
    {
        "_op_type": "index",
        "_index": "mi_indice",
        "_source": {
            "title": "Documento 2",
            "contenido": "Este es el segundo documento"
        }
    }
]

success_count, errors = es_native.bulk(actions=actions)

# We execute the bulk without helper
operations = [
    json.dumps({ "index": { "_index": "mi_indice", "_id": "1" } }),
    json.dumps({ "title": "Documento 1", "contenido": "Este es el primer documento" }),
    json.dumps({ "index": { "_index": "mi_indice", "_id": "2" } }),
    json.dumps({ "title": "Documento 2", "contenido": "Este es el segundo documento" })
]

es_native.bulk_without_helper(operations=operations, wait_for="wait_for")

# We execute the search_all
query = {
    "query": {"bool": {"must": [{"term": {"name_field": {"value": ""}}}]}},
}
es_native.search_all(body=query, index="name_index")

# We execute the msearch
searches = [
    {"index": "mi_indice"},
    {
        "query": {
            "match": {
                "contenido": "primer"
            }
        }
    },
    {"index": "mi_indice"},
    {
        "query": {
            "match": {
                "contenido": "segundo"
            }
        }
    }
]

es_native.msearch(searches=searches)

# We execute de mget
doc_ids = ["1", "2", "3"]

response = es_native.mget(index="name_index", doc_ids=doc_ids)

# We execute the count
query = {
    "query": {"bool": {"must": [{"term": {"name_field": {"value": ""}}}]}},
    
}
resp = es_native.count(index="name_index", body=query)

# We close the connection
es_native.close()

```

## License

This project is licensed under the GNU GPLv3 license. See the LICENSE file for more details.

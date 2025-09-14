from src.utils.constants import IndexFields

class QueryParser:
    """
    This class handles query parser, that converts the initial query into an Elasticsearch query.
    """
    def __init__(self, use_self_implemented=False):
        self.use_self_implemented = use_self_implemented
    
    def set_use_self_implemented(self, value):
        self.use_self_implemented = value
    
    # This only works in newer versions of Elasticsearch.
    def build_embedding_query(self, input_embedding):
        return {
            'knn': {
                'query_vector': input_embedding,
                'field': IndexFields.EMBEDDING.value
            }
        }
    
    # For older versions of Elasticsearch
    def build_dense_vector_query(self, query, input_embedding):
        return {
            "query": {
                "script_score": {
                    **query,
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0", 
                        "params": {
                            "query_vector": input_embedding
                        }
                    }
                }
            }
        }
    
    def build_query(self, input_string, only_search_title_abstract=False):
        if self.use_self_implemented:
            return self.build_query_self_implemented(input_string)
        else:
            return self.build_query_elasticsearch(input_string, only_search_title_abstract)

    def build_query_elasticsearch(self, input_string, only_search_title_abstract=False):
        query = {
            'query': {
                'query_string': {
                    'query': input_string,
                }
            }
        }
        if only_search_title_abstract:
            query['query']['query_string']['fields'] = [IndexFields.TITLE.value, IndexFields.ABSTRACT.value]
        else:
            query['query']['query_string']['default_field'] = IndexFields.FULL_TEXT.value
        return query

    def build_query_self_implemented(self, input_string):
        print("Self-implemented option removed here!")
        pass

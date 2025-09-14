from src.utils.constants import IndexFields, ES_INDEX_NAME
from src.elasticsearch_client import ElasticsearchClient


class Search:
    """
    This class handles search the iranthology Elasticsearch index.
    """
    def __init__(self, es_client: ElasticsearchClient=None):
        self.es_client = es_client
        if not self.es_client:
            self.es_client = ElasticsearchClient()
    
    def retrieve_document(self, id):
        """
        Retrieve a document given the documents index id.

        Args:
            id: Elasticsearch id of the document.

        Returns:
            Response of the Elasticsearch get operation.
        """
        return self.es_client().get(index=ES_INDEX_NAME, id=id)

    def search(self, query, from_, size):
        return self.es_client().search(index=ES_INDEX_NAME, query=query, from_=from_, size=size, rest_total_hits_as_int=True, highlight={"fields": {field.value: {} for field in IndexFields}, 'pre_tags': ['<b>'], 'post_tags': ['</b>']})
    
    # TODO: Unused method, could be deleted
    def boolean_search(self, query_args, minimum_should_match=0):
        query = {
            "bool": {
                **query_args,
                "minimum_should_match": minimum_should_match
            }
        }
        return self.search(query)

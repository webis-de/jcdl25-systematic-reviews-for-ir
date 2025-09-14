from elasticsearch import Elasticsearch
from pprint import pprint
from dotenv import load_dotenv
import os

from src.utils.constants import ES_URL

load_dotenv()


ES_USER = os.getenv('ES_USER')
ES_PASSWORD = os.getenv('ES_PASSWORD')


class ElasticsearchClient:
    """
    This class handles the Elasticsearch client instance.
    """
    def __init__(self):
        if ES_USER == None or ES_PASSWORD == None:
            raise Exception("No Authentication provided for Elasticsearch.")
        self.client = Elasticsearch(ES_URL, basic_auth=(ES_USER, ES_PASSWORD), request_timeout=30)
        client_info = self.client.info()
        print('Connected to Elasticsearch!')
        pprint(client_info.body)
    
    def __call__(self, *args, **kwds):
        return self.client

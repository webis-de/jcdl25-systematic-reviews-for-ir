#from sentence_transformers import SentenceTransformer
import re

from src.elasticsearch_client import ElasticsearchClient
from src.utils import get_all_files
from src.utils.constants import IndexFields, DATA_PATH, ES_INDEX_NAME


class Index:
    """
    This class handles the indexing of the IR Anthology with Elasticsearch.
    """
    def __init__(self, es_client: ElasticsearchClient=None):
        self.es_client = es_client
        if not self.es_client:
            self.es_client = ElasticsearchClient()
        self.model = None
    
    def reindex(self, bulk_size=100):
        """
        Reindex the Elasticsearch index.

        Args:
            bulk_size: The number of documents used in one bulk-operation. Defaults to 100.
        """
        # Reset index
        self.init_embedding_model()
        self.reset_index()
        self.update_mapping()

        # Collect and create all documents
        files = get_all_files(DATA_PATH)
        documents = [self.create_document(bib_id, info_dict) for bib_id, info_dict in files.items()]

        # Insert documents into the index
        for i in range(0, len(documents), bulk_size):
            self.insert_documents(documents[i:i+bulk_size])

        print(f"Successfully indexed {len(documents)} documents")
    
    def reset_index(self):
        """
        Resets the index by deleting the current iranthology index and recreating it.

        Returns:
            resp: Response of the Elasticsearch create operation.
        """
        self.es_client().indices.delete(index=ES_INDEX_NAME)
        resp = self.es_client().indices.create(index=ES_INDEX_NAME)
        return resp

    def update_mapping(self):
        """
        Sets the mapping of the IR Anthology index.

        Returns:
            Elasticsearch response of the mapping update.
        """
        return self.es_client().indices.put_mapping(
            index=ES_INDEX_NAME,
            properties={
                IndexFields.NAME.value: { # bib-id
                    "type": "keyword"
                },
                IndexFields.BIB_TYPE.value: {
                    "type": "keyword"
                },
                IndexFields.TITLE.value: {
                    "type": "text"
                },
                IndexFields.YEAR.value: {
                    "type": "integer"
                },
                IndexFields.BOOKTITLE.value: {
                    "type": "text"
                },
                IndexFields.SERIES.value: {
                    "type": "text"
                },
                IndexFields.AUTHOR.value: {
                    "type": "text" # Array
                },
                IndexFields.EDITOR.value: {
                    "type": "text" # Array
                },
                IndexFields.FULL_TEXT.value: {
                    "type": "text"
                },
                IndexFields.VENUE.value: {
                    "type": "text"
                },
                IndexFields.URL.value: {
                    "type": "text" # Array
                },
                IndexFields.DOI.value: {
                    "type": "text" # Array
                },
                IndexFields.OPENACCESS.value: {
                    "type": "keyword"
                },
                IndexFields.ABSTRACT.value: {
                    "type": "text"
                },
                #IndexFields.EMBEDDING.value: {
                #    "type": "dense_vector",
                #    "dims": 1536,
                #    "index": True,
                #    "similarity": "cosine"
                #}
            },
        )
    
    def insert_documents(self, documents):
        """
        Insert multiple documents into the IR anthology index.

        Args:
            documents: A list containing the documents to be inserted. Should already have the fitting format for the index.

        Returns:
            Elasticsearch response of the bulk operation.
        """
        operations = []
        for document in documents:
            operations.append({'index': {'_index': ES_INDEX_NAME}})
            operations.append({
                **document,
                #'embedding': self.get_embedding(document[IndexFields.FULL_TEXT.value])
            })
        return self.es_client().bulk(operations=operations)
    
    def create_document(self, bib_id, info_dict):
        """
        Returns the formatted document for the Elasticsearch index.

        Args:
            bib_id: Identifier in the bib-file for this paper.
            info_dict: Dict containing the data about the paper (from the get_all_files-method).

        Returns:
            Dict containing the paper as formatted for the Elasticsearch index.
        """
        document = {}
        document[IndexFields.NAME.value] = bib_id
        try:
            document[IndexFields.BIB_TYPE.value] = info_dict['bib-data'].type
        except:
            # No bib-type in the bib entry
            document[IndexFields.BIB_TYPE.value] = ""
        try:
            document[IndexFields.TITLE.value] = info_dict['bib-data'].fields['title']
        except:
            # No title in the bib entry
            document[IndexFields.TITLE.value] = ""
        try:
            document[IndexFields.YEAR.value] = info_dict['bib-data'].fields['year']
        except:
            # No year in the bib entry
            document[IndexFields.YEAR.value] = ""
        try:
            document[IndexFields.BOOKTITLE.value] = info_dict['bib-data'].fields['booktitle']
        except:
            # No booktitle in the bib entry
            document[IndexFields.BOOKTITLE.value] = ""
        try:
            document[IndexFields.SERIES.value] = info_dict['bib-data'].fields['series']
        except:
            # No series in the bib entry
            document[IndexFields.SERIES.value] = ""
        try:
            document[IndexFields.AUTHOR.value] = [str(a) for a in info_dict['bib-data'].persons[u'author']]
        except:
            # No author in the bib entry
            document[IndexFields.AUTHOR.value] = []
        try:
            document[IndexFields.EDITOR.value] = [str(a) for a in info_dict['bib-data'].persons[u'editor']]
        except:
            # No editor in the bib entry
            document[IndexFields.EDITOR.value] = []
        try:
            document[IndexFields.FULL_TEXT.value] = info_dict['full-text']
        except:
            # No full-text
            document[IndexFields.FULL_TEXT.value] = ""
        try:
            document[IndexFields.VENUE.value] = info_dict['bib-data'].fields['venue']
        except:
            # No venue in the bib entry
            document[IndexFields.VENUE.value] = ""
        try:
            document[IndexFields.URL.value] = info_dict['bib-data'].fields['url']
        except:
            # No url in the bib entry
            document[IndexFields.URL.value] = ""
        try:
            document[IndexFields.DOI.value] = info_dict['bib-data'].fields['doi']
        except:
            # No doi in the bib entry
            document[IndexFields.DOI.value] = ""
        try:
            document[IndexFields.OPENACCESS.value] = info_dict['bib-data'].fields['openaccess']
        except:
            # No openaccess in the bib entry
            document[IndexFields.OPENACCESS.value] = ""
        try:
            document[IndexFields.ABSTRACT.value] = info_dict['json-data']['abstract']
        except:
            # No abstract in the bib entry
            document[IndexFields.ABSTRACT.value] = ""

        document = self.sanity_check_document(document)
        return document
    
    def sanity_check_document(self, document):
        """
        Performs a sanity check on a document and corrects erros if possible.

        Args:
            document: Document to sanity check.

        Returns:
            Sanity checked document.
        """
        # Remove backslashes
        document[IndexFields.URL.value] = document[IndexFields.URL.value].replace('\\', '')
        document[IndexFields.DOI.value] = document[IndexFields.DOI.value].replace('\\', '')

        # Replace ERROR with empty string
        document[IndexFields.AUTHOR.value] = [author if "ERROR" not in str(author) else "" for author in document[IndexFields.AUTHOR.value]]
        document[IndexFields.EDITOR.value] = [editor if "ERROR" not in str(editor) else "" for editor in document[IndexFields.EDITOR.value]]

        # Remove Latex commands
        document[IndexFields.AUTHOR.value] = [re.sub(r'\\.*?{([^}]*)}', '\\1', author) for author in document[IndexFields.AUTHOR.value]]
        document[IndexFields.EDITOR.value] = [re.sub(r'\\.*?{([^}]*)}', '\\1', editor) for editor in document[IndexFields.EDITOR.value]]
        document[IndexFields.TITLE.value] = re.sub(r'\\.*?{([^}]*)}', '\\1', document[IndexFields.TITLE.value])

        document[IndexFields.AUTHOR.value] = [re.sub(r'{([^}]*)}', '\\1', author) for author in document[IndexFields.AUTHOR.value]]
        document[IndexFields.EDITOR.value] = [re.sub(r'{([^}]*)}', '\\1', editor) for editor in document[IndexFields.EDITOR.value]]
        document[IndexFields.TITLE.value] = re.sub(r'{([^}]*)}', '\\1', document[IndexFields.TITLE.value])

        return document
    
    def init_embedding_model(self):
        """
        Initializes the embedding model.
        """
        self.model = None#SentenceTransformer('Alibaba-NLP/gte-Qwen2-1.5B-instruct', trust_remote_code=True)
    
    def get_embedding(self, text):
        """
        Returns the embedding of the input text using a sentence transformer model.
    
        Args:
            text: The input text to get the embedding from.
    
        Returns:
            The embedding vector.
        """
        return self.model.encode(text)

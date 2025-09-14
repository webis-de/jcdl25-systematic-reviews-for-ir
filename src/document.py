from typing import Any
from src.utils.constants import IndexFields


class Document:
    """
    This class handles the documents returned from Elasticsearch.
    """
    def __init__(self, document_dict):
        self._index = document_dict['_index']
        self._id = document_dict['_id']
        self._score = document_dict['_score']
        self._source = document_dict['_source']
        try:
            self.highlight = document_dict['highlight']
            if not self.highlight[IndexFields.FULL_TEXT.value]:
                self.highlight.update({IndexFields.FULL_TEXT.value: [str(self.full_text[:300])]})
        except:
            self.highlight = {field.value: ["<em>Cannot show snippet for this query.</em>"] for field in IndexFields}
            self.highlight.update({IndexFields.FULL_TEXT.value: [str(self.full_text[:300])]})
    
    def __getattr__(self, name: str) -> Any:
        return self._source[name]
    
    def __str__(self) -> str:
        s = "-----------------------------------------------------------------------\n"
        for field in IndexFields:
            s += f"{field.value}: {self._source[field.value]}\n"
        s += "-----------------------------------------------------------------------"
        return s
    
    def get_highlight(self, field: str):
        return self.highlight[field]

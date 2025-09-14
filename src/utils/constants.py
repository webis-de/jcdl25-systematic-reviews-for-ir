from enum import Enum


DATA_PATH=None
ES_URL=None
ES_INDEX_NAME=None


class IndexFields(Enum):
    NAME = "name"
    BIB_TYPE = "bib_type"
    TITLE = "title"
    YEAR = "year"
    BOOKTITLE = "booktitle"
    SERIES = "series"
    AUTHOR = "author"
    EDITOR = "editor"
    FULL_TEXT = "full_text"
    VENUE = "venue"
    URL = "url"
    DOI = "doi"
    OPENACCESS = "openaccess"
    EMBEDDING = "embedding"
    ABSTRACT = "abstract"

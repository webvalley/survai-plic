"""
"""
from abc import ABC, abstractmethod

# ==================
# Crawler Exceptions
# ==================

DOI_NOT_FOUND_ERROR = 'Article Not Found by provided ID'
NO_METADATA_ERROR = 'No Metadata found for Document'


# ======================
# Crawler Abstract Class
# ======================

class PaperIDNotFoundError(RuntimeError):
    def __init__(self, *args, **kwargs):
        defs = {}.update(**kwargs)
        super().__init__(DOI_NOT_FOUND_ERROR, *args, defs)


class ArticleMetadataError(RuntimeError):
    def __init__(self, *args, **kwargs):
        defs = {}.update(**kwargs)
        super().__init__(NO_METADATA_ERROR, *args, defs)


class MetadataCrawler(ABC):

    def __init__(self, paper_id: str, metadata_engine: str):
        self._id: str = paper_id
        self._engine = metadata_engine
        self._paper_metadata = None

    @property
    def metadata(self):
        """"""
        if self._paper_metadata:
            return self._paper_metadata
        return self.retrieve_paper_metadata()

    def retrieve_paper_metadata(self):
        """"""
        article = self._search_paper_by_id()
        if article is None:
            raise PaperIDNotFoundError()
        article_found, metadata = self._fetch_metadata(article)
        if not article_found:
            raise ArticleMetadataError()
        self._paper_metadata = metadata
        return metadata

    def crawl_paper(self, paper_instance=None):
        """"""
        if not self._paper_metadata:
            self.retrieve_paper_metadata()

        paper = self._collect_paper_data(paper_instance)
        return paper

    @abstractmethod
    def validate(self, paper_id):
        pass

    # -----------
    # Private API
    # -----------

    @staticmethod
    def _to_list(x):
        if x is None or isinstance(x, list):
            return x
        return [x]

    @abstractmethod
    def _collect_paper_data(self, paper_instance=None):
        """main procedure to process paper metadata and
        generate/update a new Paper model instance.
        """
        pass

    @abstractmethod
    def _search_paper_by_id(self):
        pass

    @abstractmethod
    def _fetch_metadata(self, article):
        pass

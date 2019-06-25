"""

"""

from ..models import ARXIV_ENGINE, SCOPUS_ENGINE, SEMANTIC_SCHOLAR_ENGINE, MANUAL_ENTRY
from .base import PaperIDNotFoundError, ArticleMetadataError, MetadataCrawler
from .scopus_crawler import ScopusCrawler
from .arxiv_crawler import ArxivCrawler
from .semantic_scholar_crawler import SemanticScholarCrawler

CRAWLERS = {
    SCOPUS_ENGINE: ScopusCrawler,
    ARXIV_ENGINE: ArxivCrawler,
    SEMANTIC_SCHOLAR_ENGINE: SemanticScholarCrawler,
    MANUAL_ENTRY: None
}


def instantiate_crawler(id, metadata_engine):
    """"""
    try:
        crawler_cls = CRAWLERS.get(metadata_engine)
    except KeyError as e:
        raise KeyError('The provided Metadata Engine is wrong: {}'.format(str(e)))
    else:
        crawler = None if crawler_cls is None else crawler_cls(id, metadata_engine)
        return crawler

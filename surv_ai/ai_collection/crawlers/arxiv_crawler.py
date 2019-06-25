"""
Paper Crawler downloading metadata information
using ArXiv (`pyarxiv` Python Module)
"""

from .semantic_scholar_crawler import SemanticScholarCrawler
from ..models import Keyword
from arxiv import query as arxiv_query
from datetime import datetime
from requests import get as get_request
from urllib.request import urljoin


class ArxivCrawler(SemanticScholarCrawler):
    ARXIV_VALIDATE_URL_PREFIX = 'https://arxiv.org/abs/'

    # -------------------
    # ArXiv Metadata Keys
    # -------------------
    TAGS_KEY = 'tags'
    TAG_LABEL = 'label'
    TAG_NAME = 'term'

    PAPER_ABSTRACT = 'summary'
    PUBLISHED_DATE = 'published'

    def __init__(self, paper_id, metadata_engine):
        self._arxiv_metadata = None
        super().__init__(paper_id, metadata_engine)

    def validate(self, paper_id):
        url_prefix = self.ARXIV_VALIDATE_URL_PREFIX
        if not paper_id.startswith(url_prefix):
            paper_ref = urljoin(url_prefix, paper_id)
        else:
            paper_ref = paper_id
        r = get_request(paper_ref)
        return (r.status_code == 200)

    def retrieve_paper_metadata(self):
        metadata = super().retrieve_paper_metadata()
        self._arxiv_metadata = self._get_arxiv_metadata()
        return metadata

    def _get_arxiv_metadata(self):
        try:
            paper_info = arxiv_query(self._id)
            if paper_info and len(paper_info):
                return paper_info[0]
            return None
        except:
            return None

    def _collect_paper_data(self, paper_instance=None):
        """"""
        paper = super()._collect_paper_data(paper_instance=paper_instance)
        if self._arxiv_metadata:
            self._complement_paper_information(paper)
        return paper

    def _complement_paper_information(self, paper):
        """Complete Paper information as gathered from ARXIV"""

        try:
            # 1. Keywords & Terms
            # -------------------
            self._update_paper_terms(paper)
            # 2. CoreData
            # -----------
            self._update_publication_info(paper)

        except KeyError as e:
            raise e

    def _update_publication_info(self, paper):
        """"""
        paper.abstract = self._arxiv_metadata.get(self.PAPER_ABSTRACT, '')
        paper_pub_date = self._arxiv_metadata.get(self.PUBLISHED_DATE, '')
        if paper_pub_date:
            paper.publication_date = datetime.strptime(paper_pub_date, '%Y-%m-%dT%H:%M:%SZ')
            paper.save(update_fields=['publication_date', 'abstract'])
        else:
            paper.save(update_fields=['abstract', ])

    def _update_paper_terms(self, paper):
        """
        """
        try:
            tags = self._arxiv_metadata.get(self.TAGS_KEY, [])
            terms_collection = []
            for tag in tags:
                term = tag.get(self.TAG_NAME, '')
                label = tag.get(self.TAG_LABEL, '')
                kw_name = label if label else term
                kw_instance, created = Keyword.objects.get_or_create(name=kw_name.lower())
                if created:
                    kw_instance.save()
                terms_collection.append(kw_instance)
        except KeyError as e:
            raise KeyError('Error in Retrieving Metadata Key for Authors: {}'.format(str(e)))
        else:
            for term in terms_collection:
                paper.terms.add(term)
            paper.save()

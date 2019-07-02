from .base import MetadataCrawler
from ..models import ARXIV_ENGINE, SCOPUS_ENGINE, SEMANTIC_SCHOLAR_ENGINE
from ..models import Keyword, Author, Paper, AuthorPaper
import requests
from string import punctuation


class SemanticScholarCrawler(MetadataCrawler):
    PAPER_URL = 'https://api.semanticscholar.org/v1/paper/{ID}'

    TOPICS_KEY = 'topics'
    AUTHORS_KEY = 'authors'
    DOI_KEY = 'doi'
    ARXIVID_KEY = 'arxivId'
    PAPERID_KEY = 'paperId'
    TITLE_KEY = 'title'
    URL_KEY = 'url'
    VENUE_KEY = 'venue'
    YEAR_KEY = 'year'

    def __init__(self, paper_id: str, metadata_engine: str):
        super().__init__(paper_id, metadata_engine)
        self._authors_paper_list = None

    def validate(self, paper_id):
        paper_ref = self.PAPER_URL.format(ID=paper_id)
        r = requests.get(paper_ref)
        return (r.status_code == 200)

    def _search_paper_by_id(self):
        if self._engine == ARXIV_ENGINE:
            response = self._get_by_arxivid()
        elif self._engine == SCOPUS_ENGINE:
            response = self._get_by_doi()
        elif self._engine == SEMANTIC_SCHOLAR_ENGINE:
            response = self._get_by_semantic_scholar_id()
        else:
            raise ValueError('Error: Specified metadata engine {} '
                             'is not supported.'.format(self._engine))

        if response and response.status_code == 200:
            return response
        return None  # In case of errors, return None

    def _get_by_arxivid(self):
        """"""
        if not self._id.startswith('arXiv:'):
            paper_id = 'arXiv:{}'.format(self._id)
        else:
            paper_id = self._id
        paper_reference_url = self.PAPER_URL.format(ID=paper_id)
        return requests.get(paper_reference_url)

    def _get_by_doi(self):
        """"""
        paper_reference_url = self.PAPER_URL.format(ID=self._id)
        return requests.get(paper_reference_url)

    def _get_by_semantic_scholar_id(self):
        """"""
        paper_url = self.PAPER_URL.format(ID=self._id)
        return requests.get(paper_url)

    def _fetch_metadata(self, article):
        """
        Returns paper Metadata.

        In this case, `article` is the response object
        returned by the requests GET.
        """
        try:
            return True, article.json()
        except:
            return False, None

    def _collect_paper_data(self, paper_instance=None):
        """
        Process Metadata as returned by SemanticScholar APIs.

        The keys (of interest) in the JSON object as returned by the API are:
        - 'arxivId': ID or ArXiv (if any)
        - 'authors': List of Dict containing ('authorId', 'name', 'url') fields
        - 'doi': DOI of the paper (if any)
        - 'paperId': SemanticScholar Paper ID (if any)
        - 'title': title of the paper
        - 'topics': List of Dic containing ('topic', 'topicId', 'url')
        - 'url': SemanticScholar URL for the Paper
        - 'venue': Venue where the paper has been published. "Arxiv" if it is an ARXIV paper.
        - 'year': Year of Publication
        """

        try:
            # 1. Collect Paper Terms
            # ----------------------
            keywords = self._extract_paper_terms()

            # 2. Extract Authors
            # ------------------
            authors_map = self._extract_paper_authors()

        except KeyError as e:
            raise e
        else:
            # 3. Create Paper
            # ---------------
            paper = self._create_paper_entry(keywords, authors_map, paper_instance)
            return paper

    def _extract_paper_terms(self):
        """"""
        TERM_KEY = 'topic'
        try:
            topic_collection = list()
            topics = self._paper_metadata.get(self.TOPICS_KEY)
            topics = self._to_list(topics)
            for topic in topics:
                term = topic.get(TERM_KEY)
                kw_instance, created = Keyword.objects.get_or_create(name=term.lower())
                if created:
                    kw_instance.save()
                topic_collection.append(kw_instance)
        except KeyError as e:
            raise KeyError('Error in Retrieving Metadata Key for Topics: {}'.format(str(e)))
        else:
            return topic_collection

    def _extract_paper_authors(self):
        """"""
        AUTHOR_NAME_KEY = 'name'

        try:
            authors_map = dict()
            authors = self._paper_metadata.get(self.AUTHORS_KEY)
            authors = self._to_list(authors)
            for order, author in enumerate(authors):
                name = author.get(AUTHOR_NAME_KEY)
                name = self._sanitise_author_name(name)
                auth_instance, created = Author.objects.get_or_create(name__iexact=name)
                if created:
                    auth_instance.name = name
                    auth_instance.save()
                authors_map[(order + 1)] = auth_instance
        except KeyError as e:
            raise KeyError('Error in Retrieving Metadata Key for Authors: {}'.format(str(e)))
        else:
            return authors_map

    def _sanitise_author_name(self, name):
        """Sanitisation function for authors' name"""
        n = name.strip()
        for p in punctuation:
            n = n.replace(p, '')
        return n

    def _create_paper_entry(self, keywords_collection, authors_map,
                            paper_instance=None):
        """"""

        if paper_instance is None:
            paper = Paper(reference_id=self._id,
                          metadata_reference=self._engine)
        else:
            paper = paper_instance

        try:
            paper.venue = self._paper_metadata.get(self.VENUE_KEY)
            paper.year_of_publication = self._paper_metadata.get(self.YEAR_KEY)
            paper.title = self._paper_metadata.get(self.TITLE_KEY)

            paper.doi = self._paper_metadata.get(self.DOI_KEY, '')
            paper.ss_id = self._paper_metadata.get(self.PAPERID_KEY, '')
            paper.arxiv_id = self._paper_metadata.get(self.ARXIVID_KEY, '')
            paper.ss_url = self._paper_metadata.get(self.URL_KEY, '')

            paper.save()
        except KeyError as e:
            raise KeyError('Error in Retrieving Metadata Key for Paper Core Data: {}'.format(str(e)))

        else:
            # Add Terms
            for kw in keywords_collection:
                paper.terms.add(kw)

            authors_paper_list = list()
            for sequence, author in authors_map.items():
                author_paper = AuthorPaper(paper=paper, author=author)
                author_paper.author_order = sequence
                author_paper.save()
                authors_paper_list.append(author_paper)

            if len(authors_paper_list):
                self._authors_paper_list = authors_paper_list

            # Update Keywords and Authors
            paper.save()

            return paper

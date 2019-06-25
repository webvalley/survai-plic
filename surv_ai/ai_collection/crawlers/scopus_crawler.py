"""
Paper Crawler downloading metadata information
using Elsevier API (`elsapy` Python Module)
"""
from ..models import Keyword, Affiliation
from .semantic_scholar_crawler import SemanticScholarCrawler

from elsapy.elsdoc import AbsDoc
from elsapy.elssearch import ElsSearch
from elsapy.elsclient import ElsClient
from requests import get as get_request


# ====================================
# Crawler Main Functions and Utilities
# ====================================

class ScopusCrawler(SemanticScholarCrawler):
    """"""
    CROSSREF_API_VALIDATE_URL_SCHEMA = 'https://api.crossref.org/works/{doi}/agency'

    # ----------------
    # Elsevier API KEY
    # ----------------
    API_KEY = '619e44f5544b25eaf722710a62982d46'

    # -----------------------
    # Metadata processing Key
    # -----------------------
    AFFILIATION_KEY = 'affiliation'
    AUTHKEYWORDS_KEY = 'authkeywords'
    IDXTERMS_KEY = 'idxterms'
    SUBJECT_AREAS_KEY = 'subject-areas'
    AUTHORS_KEYS = 'authors'
    COREDATA_KEY = 'coredata'

    # -------------------------
    # Affiliation Metadata Keys
    # -------------------------
    AFFILIATION_CITY = 'affiliation-city'
    AFFILIATION_ID = '@id'
    AFFILIATION_NAME = 'affilname'
    AFFILIATION_COUNTRY = 'affiliation-country'

    # --------------------------------
    # Keywords and Terms Metadata Keys
    # --------------------------------
    AUTH_KEYWORD_RES_DICT_KEY = 'author-keyword'
    IDX_TERM_RES_DICT_KEY = 'mainterm'
    SUBJECT_RES_DICT_KEY = 'subject-area'
    NAME_KEY = '$'

    # ----------------------
    # Authors Metadata Keys
    # ----------------------
    AUTHORS_RES_DICT_KEY = 'author'
    # ------ Single author data
    AUTHOR_FIRST_NAME = 'ce:given-name'
    AUTHOR_SURNAME = 'ce:surname'
    AUTHOR_INDEXED_NAME = 'ce:indexed-name'
    AUTHOR_SEQ_ORDER = '@seq'
    AUTHOR_AFFILIATION = 'affiliation'
    AUTHOR_AFFILIATION_ID = '@id'

    # -------------------
    # Paper Metadata Keys
    # -------------------
    DOI_KEY = 'prism:doi'
    PUB_NAME = 'prism:publicationName'  # Journal
    SUBMISSION_TYPE = 'subtypeDescription'
    ISSN = 'prism:issn'
    PAGE_RANGE = 'prism:pageRange'
    VOLUME = 'prism:volume'
    CITEDBY_COUNT = 'citedby-count'
    EID = 'eid'
    PUBMED_ID = 'pubmed-id'
    PAPER_ABSTRACT = 'dc:description'
    PAPER_TITLE = 'dc:title'
    COVER_DATE = 'prism:coverDate'  # publication_date
    AGGREGATION_TYPE = 'prism:aggregationType'

    def __init__(self, paper_id, metadata_engine):
        self.client = ElsClient(self.API_KEY)
        self._scopus_metadata = None
        super().__init__(paper_id, metadata_engine)

    def validate(self, paper_id):
        paper_ref = self.CROSSREF_API_VALIDATE_URL_SCHEMA.format(doi=paper_id)
        r = get_request(paper_ref)
        return (r.status_code == 200)

    @property
    def scopus_available(self):
        if self._scopus_metadata is None:
            return False
        return self.AUTHKEYWORDS_KEY in self._scopus_metadata.keys()

    def retrieve_paper_metadata(self):
        metadata = super().retrieve_paper_metadata()
        self._scopus_metadata = self._get_scopus_metadata()
        return metadata

    def _get_scopus_metadata(self):
        """"""
        # 1. Search Paper using DOI
        # -------------------------
        search = ElsSearch(self._id, 'scopus')
        search.execute(self.client, get_all=True)
        article = None
        for res in search.results:
            if res.get('prism:doi', '') == self._id:
                article = res
                break

        if article is None:
            return None

        # 2. Get Paper Metadata from Scopus
        # ---------------------------------
        scopus_id = article.get('dc:identifier', None)
        if scopus_id is None:
            return None
        scopus_id = scopus_id.replace('SCOPUS_ID:', '')
        doc = AbsDoc(scp_id=scopus_id)
        data_available = doc.read(self.client)
        doc_data = None if not data_available else doc.data
        return doc_data

    def _collect_paper_data(self, paper_instance=None):
        """"""
        paper = super()._collect_paper_data(paper_instance=paper_instance)
        if self.scopus_available:
            self._complement_paper_information(paper)
        return paper

    def _complement_paper_information(self, paper):
        """Complete Paper information as gathered from SCOPUS"""
        try:
            # 1. Keywords & Terms
            # -------------------
            self._update_paper_terms(paper)

            # 2.1. Affiliations
            # -----------------
            affiliations_map = self._collect_authors_affiliations()

            # 2.2. Complete Authors Affiliation info
            # ---------------------------------------
            self._add_affiliations_to_authors(affiliations_map, paper)

            # 3. CoreData
            # -----------
            self._update_publication_info(paper)
        except KeyError as e:
            raise e

    def _update_publication_info(self, paper):
        """"""
        scd = self._scopus_metadata.get(self.COREDATA_KEY, {})
        if len(scd):
            paper.abstract = scd.get(self.PAPER_ABSTRACT, '')
            # Blanks is allowed for the following attributes
            paper.doi = scd.get(self.DOI_KEY, '')
            paper.issn = scd.get(self.ISSN, '')
            paper.page_range = scd.get(self.PAGE_RANGE, '')
            paper.article_type = scd.get(self.PUB_NAME, '')
            paper.aggregation_type = scd.get(self.AGGREGATION_TYPE, '')
            paper.volume = scd.get(self.VOLUME, '')
            paper.eid = scd.get(self.EID, '')
            paper.pubmed_id = scd.get(self.PUBMED_ID, '')
            paper.publication_date = scd.get(self.COVER_DATE, '')
            paper.save(update_fields=['doi', 'issn', 'page_range', 'article_type',
                                      'aggregation_type', 'volume', 'eid', 'pubmed_id',
                                      'publication_date', 'abstract'])

    def _collect_authors_affiliations(self):
        """
        """
        try:
            affiliation_data = self._to_list(self._scopus_metadata.get(self.AFFILIATION_KEY, []))

            if affiliation_data is None:
                return dict()

            affiliations = dict()
            for entry in affiliation_data:
                aff_id = entry.get(self.AFFILIATION_ID, '')
                aff_city = entry.get(self.AFFILIATION_CITY, '')
                aff_country = entry.get(self.AFFILIATION_COUNTRY, '')
                aff_name = entry.get(self.AFFILIATION_NAME, '')
                affiliation, created = Affiliation.objects.get_or_create(name=aff_name)
                if created:
                    affiliation.city = aff_city
                    affiliation.country = aff_country
                    affiliation.save()
                affiliations[aff_id] = affiliation
            return affiliations
        except KeyError as e:
            raise KeyError('Error in Retrieving Metadata Key for Affiliations: {}'.format(str(e)))

    def _add_affiliations_to_authors(self, affiliations_map, paper):
        """"""
        authors_map = dict()
        try:
            authors_data = self._scopus_metadata.get(self.AUTHORS_KEYS, dict())

            if authors_data is None or not len(authors_data):
                return dict()

            authors_data = self._to_list(authors_data.get(self.AUTHORS_RES_DICT_KEY, None))
            for auth_data in authors_data:
                # None of the following attribute is optional in the model
                first_name = auth_data.get(self.AUTHOR_FIRST_NAME, '')
                surname = auth_data.get(self.AUTHOR_SURNAME, '')
                indexed_name = auth_data.get(self.AUTHOR_INDEXED_NAME, '')

                name = '{} {}'.format(first_name, surname)
                author_info = self._fetch_author_paper(author_name=name)
                if author_info is None:
                    continue

                author = author_info.author
                author.indexed_name = indexed_name
                author.save(update_fields=['indexed_name'])

                # add affiliation
                if affiliations_map and len(affiliations_map):
                    affiliation_ref = self._to_list(auth_data.get(self.AUTHOR_AFFILIATION))
                    _aff_added = False
                    if affiliation_ref is None:
                        continue
                    for aff_info in affiliation_ref:
                        aff_id = aff_info.get(self.AUTHOR_AFFILIATION_ID, '')
                        try:
                            affiliation_instance = affiliations_map.get(aff_id, None)
                        except KeyError:
                            raise KeyError('AffiliationID {} not found in MAP'.format(aff_id))
                        else:
                            author_info.affiliations.add(affiliation_instance)
                            _aff_added = True
                    if _aff_added:
                        author_info.save()
        except KeyError as e:
            raise KeyError('Error in Retrieving Metadata Key for Authors: {}'.format(str(e)))

    def _fetch_author_paper(self, author_name):
        if self._authors_paper_list is None:
            return None
        for author_paper in self._authors_paper_list:
            if author_paper.author.name.lower() == author_name.lower():
                return author_paper
        return None

    def _update_paper_terms(self, paper):
        """
        """
        try:
            keywords_data = self._scopus_metadata.get(self.AUTHKEYWORDS_KEY, [])
            idx_terms_data = self._scopus_metadata.get(self.IDXTERMS_KEY, [])
            subject_areas = self._scopus_metadata.get(self.SUBJECT_AREAS_KEY, [])

            kw_set = self._collect(keywords_data, key=self.AUTH_KEYWORD_RES_DICT_KEY)
            idx_set = self._collect(idx_terms_data, key=self.IDX_TERM_RES_DICT_KEY)
            area_set = self._collect(subject_areas, key=self.SUBJECT_RES_DICT_KEY)
            paper_terms = kw_set.union(idx_set).union(area_set)
            terms_collection = []
            for kw in paper_terms:
                kw_instance, created = Keyword.objects.get_or_create(name=kw.lower())
                if created:
                    kw_instance.save()
                terms_collection.append(kw_instance)

        except KeyError as e:
            raise KeyError('Error in Retrieving Metadata Key for Authors: {}'.format(str(e)))
        else:
            for term in terms_collection:
                paper.terms.add(term)
            paper.save()

    def _collect(self, keywords_data, key):
        """"""
        if keywords_data is None:
            return set()

        terms = list()
        keywords = self._to_list(keywords_data.get(key, None))
        for kw in keywords:
            name = kw.get(self.NAME_KEY, '').strip()
            if name:
                terms.append(name)
        return set(terms)

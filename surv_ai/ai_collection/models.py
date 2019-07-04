from django.db import models
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

from markdownx.models import MarkdownxField
from django_resumable.fields import ResumableFileField
import os

from  django.core.exceptions import ValidationError
from django.db import models
from django import forms
from django.utils.translation import gettext_lazy as _

# ========================
# Papers Model Information
# ========================
DEFAULT_MANUAL_PAPER_ENTRY = 'MANUAL_ENTRY'
BADGE_PATHOLOGY = 'badge-info'
BADGE_METHOD = 'badge-success'
BADGE_KEYWORD = 'badge-primary'

MANUAL_ENTRY = 'MANUAL'
ARXIV_ENGINE = 'ARXIV'
SCOPUS_ENGINE = 'SCOPUS'
SEMANTIC_SCHOLAR_ENGINE = 'SEMSCL'

PAPER_METADATA_REFERENCE = (
    (SCOPUS_ENGINE, 'SCOPUS/PUBMED'),
    (ARXIV_ENGINE, 'ARXIV'),
    (SEMANTIC_SCHOLAR_ENGINE, 'SEMANTIC SCHOLAR'),
    (MANUAL_ENTRY, MANUAL_ENTRY)
)

DATA_TYPES_CHOICES = (
    ('BIN', 'Binary (e.g. MatLab Files)'),
    ('IMG', 'RGB Images (e.g. JPEG, PNG)'),
    ('MED', 'Medical Images (e.g. NIFTI, DICOM)'),
    ('TXT', 'Textual (e.g. Excel, CSV)'),
    ('MIS', 'Miscellanea (see Notes)'),
    ('OTH', 'Other & Misc')
)

# =========================
# Dataset Model Information
# =========================

PATIENTS_CHOICES = (
    ('', '--------------'),
    ('ALL', 'Healthy Patients & Patients w/ Pathology'),
    ('PAT', 'Patients w/ Pathology only'),
)

# =======================
# Pathology Model Choices
# =======================
PATHOLOGY_CATEGORY_DEFAULT = 'UNKNOWN'
PATHOLOGY_CATEGORY_DEFAULT_DISPLAY = 'NOT SPECIFIED'


# ===================
# upload_to functions
# ===================

def paper_upload_path(instance, filename):
    """upload_to function to be used with Paper model instances:

    Files will be uploaded to MEDIA_ROOT/papers/<filename>
    Filename of the paper file will be composed as:
    year_first-author-last-name_title.pdf (or whatever the original extension is)
    """
    _, ext = os.path.splitext(filename)
    filename = '{fname}{e}'.format(fname=instance.paper_file_name, e=ext)
    path = os.path.join('papers', filename)
    return path


def archive_upload_path(instance, filename):
    """upload_to function to be used with DataArchive instances

    Files will be uploaded to MEDIA_ROOT/datasets/<dataset_name>/filename
    """
    return os.path.join('datasets', instance.dataset.short_name, filename)


# =================================
#   ---- Tag-based Models ----
# Configurations and Model Classes
# =================================

@mark_safe
def _display_badge(color_class, text='Resource Tag'):
    return '<span class="badge badge-pill {}">{}</span>'.format(color_class, text)


BS_CLASSES = (
    ('badge-primary', _display_badge('badge-primary')),
    ('badge-secondary', _display_badge('badge-secondary')),
    ('badge-success', _display_badge('badge-success')),
    ('badge-danger', _display_badge('badge-danger')),
    ('badge-warning', _display_badge('badge-warning')),
    ('badge-info', _display_badge('badge-info')),
    ('badge-light', _display_badge('badge-light')),
    ('badge-dark', _display_badge('badge-dark')),
    ('pink', _display_badge('pink')),
    ('indigo', _display_badge('indigo')),
    ('purple', _display_badge('purple')),
    ('orange', _display_badge('orange')),
    ('green', _display_badge('green')),
    ('blue-twitter', _display_badge('blue-twitter')),
)



class BadgeModel(models.Model):
    badge_class = models.CharField(verbose_name='Badge', choices=BS_CLASSES,
                                   default='', max_length=20)

    class Meta:
        abstract = True


class AzureKey(models.Model):

    name = models.CharField(max_length=50,verbose_name='Azure Keyphrases')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.name = self.name.replace('/', ' ').lower()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name.title()

    def __repr__(self):
        return str(self)

    class Meta:
        ordering = ['name']
        verbose_name = 'Azure Keyphrase'
        verbose_name_plural = 'Azure Keyphrases'


class Topic(BadgeModel):
    """Topic"""

    name = models.CharField(max_length=200, verbose_name='Topic',
                            unique=True, primary_key=True,
                            help_text='Note: The name of the Topic will be saved as lowercase to simplify research')

    # category = models.ForeignKey(PathologyCategory, related_name='topics',
    #                             blank=True, null=True, on_delete=models.SET_NULL)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.name = self.name.lower()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name.title()

    def __repr__(self):
        return str(self)

    def get_absolute_url(self):
        return reverse('topic_resources', args=[str(self.name)])

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model),
                       args=(self.name,))

    #def get_category_absolute_url(self):
    #    if self.category:
    #        return self.category.get_absolute_url()
    #    return ''
    
    @property
    def badge(self):
        return _display_badge(self.badge_class, self.name.title())


    #@property
    #def badge_category(self):
    #    if self.category:
    #        return self.category.badge
    #    return _display_badge('badge-dark', 'No Category')

    @staticmethod
    def badge_choices():
        return BS_CLASSES

    class Meta:
        ordering = ['name']
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'



class Keyword(BadgeModel):
    """Paper Keyword"""

    name = models.CharField(verbose_name='Keyword', max_length=250, unique=True,
                            help_text='Note: The name of the Tag will be saved as lowercase to simplify research')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.name = self.name.replace('/', ' ').lower()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name.title()

    def __repr__(self):
        return str(self)

    def get_absolute_url(self):
        return reverse('tag_resources', args=[str(self.name)])

    @property
    def badge(self):
        return _display_badge(BADGE_KEYWORD, self.name.title())

    @staticmethod
    def badge_choices():
        return [(BADGE_KEYWORD, _display_badge(BADGE_KEYWORD))]

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']


class Method(BadgeModel):
    """Paper Method"""
    name = models.CharField(max_length=200, verbose_name='Method',
                            unique=True, primary_key=True,
                            help_text='Note: The name of the Method will be saved as lowercase to simplify research')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.name = self.name.lower()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name.title()

    def __repr__(self):
        return str(self)

    def get_absolute_url(self):
        return reverse('method_studies', args=[str(self.name)])

    @property
    def badge(self):
        return _display_badge(BADGE_METHOD, self.name.title())

    @staticmethod
    def badge_choices():
        return [(BADGE_METHOD, _display_badge(BADGE_METHOD))]

    @property
    def papers(self):
        return self.studies.distinct('paper__title')

    @property
    def datasets(self):
        return self.studies.distinct('dataset__short_name')

    class Meta:
        verbose_name_plural = 'Algorithms'
        verbose_name = 'Algorithm'
        ordering = ['name']


class PathologyCategory(BadgeModel):
    name = models.CharField(verbose_name='Category', max_length=250, unique=True,
                            help_text='Note: The name of the Pathology Category will be saved as lowercase to simplify research')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.name = self.name.lower()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name.title()

    def __repr__(self):
        return str(self)

    def get_absolute_url(self):
        return reverse('pathology_category_resources', args=[str(self.name)])

    @property
    def badge(self):
        return _display_badge(self.badge_class, self.name.title())

    @staticmethod
    def badge_choices():
        return BS_CLASSES

    class Meta:
        verbose_name = 'Pathology Category'
        verbose_name_plural = 'Pathology Categories'
        ordering = ['name']


class Pathology(BadgeModel):
    """Pathology"""

    name = models.CharField(max_length=200, verbose_name='Pathology',
                            unique=True, primary_key=True,
                            help_text='Note: The name of the Pathology will be saved as lowercase to simplify research')

    category = models.ForeignKey(PathologyCategory, related_name='pathologies',
                                 blank=True, null=True, on_delete=models.SET_NULL)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.name = self.name.lower()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name.title()

    def __repr__(self):
        return str(self)

    def get_absolute_url(self):
        return reverse('pathology_resources', args=[str(self.name)])

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model),
                       args=(self.name,))

    def get_category_absolute_url(self):
        if self.category:
            return self.category.get_absolute_url()
        return ''

    @property
    def papers_percent(self):
        p_count = Paper.objects.count()
        p_perc = (self.papers.count() * 100) // p_count
        return p_perc

    @property
    def dataset_percent(self):
        d_count = Dataset.objects.count()
        d_perc = (self.datasets.count() * 100) // d_count
        return d_perc

    @property
    def badge(self):
        return _display_badge(BADGE_PATHOLOGY, str(self))

    @property
    def badge_category(self):
        if self.category:
            return self.category.badge
        return _display_badge('badge-dark', 'No Category')

    @staticmethod
    def badge_choices():
        return [(BADGE_PATHOLOGY, _display_badge(BADGE_PATHOLOGY))]

    class Meta:
        ordering = ['name']
        verbose_name = 'Pathology'
        verbose_name_plural = 'Pathologies'


# ===================================================
# Papers Section:
# Data and Metadata related to papers
# (mostly handled autom-magically) whenever possible
# ===================================================

class Author(models.Model):
    """Paper Author"""

    name = models.CharField(max_length=200, verbose_name='Author Full Name')
    indexed_name = models.CharField(max_length=200, blank=True,
                                    verbose_name='Scopus Indexed Name', )

    def __str__(self):
        return 'Author: {}'.format(self.name, self.indexed_name)

    def __repr__(self):
        return str(self)


class Paper(models.Model):
    """Research Paper"""

    metadata_reference = models.CharField(max_length=6, verbose_name='Metadata Engine',
                                          choices=PAPER_METADATA_REFERENCE)

    reference_id = models.CharField(max_length=200, verbose_name='ID',
                                    default=' ', unique=True,
                                    help_text='Unique ID for the Paper '
                                              '(i.e. DOI, Semantic Scholar ID, or ArxivID)')

    # Actual Paper Info
    title = models.CharField(max_length=300, verbose_name='Title')
    abstract = MarkdownxField(verbose_name='Abstract - Summary', blank=True)
    # Attachment
    paper_file = models.FileField(verbose_name='Paper File', null=True, blank=True,
                                  upload_to=paper_upload_path)

    # Scopus Paper meta information
    # Note: allowing BLANKS as this data comes from SemanticScholar/Elsevier/Arxiv API

    # -- General Paper Information -- shared by all metadata engines
    venue = models.CharField(max_length=300, verbose_name='Venue/Journal Name', blank=True,
                             null=True,
                             help_text='(Optional) Name of the Venue/Journal where '
                                       'the paper has been released.')
    paper_url = models.URLField(verbose_name='Paper URL', blank=True, null=True,
                                help_text='(Optional) Reference URL of the Paper')
    year_of_publication = models.PositiveSmallIntegerField(verbose_name='Year of Publication',
                                                           blank=True, null=True)

    # Elsevier/Scopus metadata (Optional)
    doi = models.CharField(max_length=200, verbose_name='DOI', unique=True, blank=True, null=True)
    issn = models.CharField(max_length=200, verbose_name='ISSN', blank=True)
    page_range = models.CharField(max_length=200, verbose_name='Page Range', blank=True)
    article_type = models.CharField(max_length=200, verbose_name='Submission Type', blank=True)
    aggregation_type = models.CharField(max_length=200, verbose_name='Article Type', blank=True)
    volume = models.CharField(max_length=200, verbose_name='Volume', blank=True)
    eid = models.CharField(max_length=200, verbose_name='EID', blank=True)
    pubmed_id = models.CharField(max_length=200, verbose_name='PubMed ID', blank=True)
    publication_date = models.DateField(verbose_name='Publication Date',blank=True,null=True)

    # ArXiv metadata (Optional)
    arxiv_id = models.CharField(max_length=200, verbose_name='ArXiv ID', blank=True, null=True)

    # SemanticScholar metadata (Optional)
    ss_id = models.CharField(max_length=200, verbose_name='Semantic Scholar Paper ID',
                             blank=True, null=True)
    ss_url = models.URLField(verbose_name='SemanticScholar URL',
                             blank=True, null=True)

    authors = models.ManyToManyField(to=Author, related_name='papers',
                                     through='AuthorPaper',
                                     through_fields=('paper', 'author'), )

    # Tag References
    terms = models.ManyToManyField(Keyword, related_name='papers', verbose_name='Keywords')

    pathology = models.ForeignKey(Pathology, verbose_name='Pathology', null=True, blank=True,
                                  related_name='papers', on_delete=models.SET_NULL)
    
    #Topic
    topic = models.ForeignKey(Topic, verbose_name='Topic',blank=True,null=True, related_name='papers', on_delete=models.SET_NULL)

    azure_keys = models.ManyToManyField(AzureKey,related_name='papers',verbose_name='Azure Keys',blank=True)
    update_azure_keys = models.BooleanField(default=True, verbose_name='Update Azure keys')

    # Upload Statistics
    upload_date = models.DateField(editable=False, auto_now_add=True)
    last_change = models.DateTimeField(editable=False, auto_now=True)

    #def save(self):
    #    if self.title is not None:
    #        super().save()
    #        if self.pathology is None and self.topic is None:
    #            raise ValidationError(_('You must indicate the Pathology or the Topic'))

    def clean(self):
        # test the rate limit by passing in the cached user object  # use your throttling utility here7
        if self.title:
            if self.pathology is None and self.topic is None:
                raise forms.ValidationError("You must indicate either the Pathology or the Topic")
            if self.publication_date is None:
                raise forms.ValidationError("You must specify the publication date!")
        return super().clean()

    @property
    def filename(self):
        _, tail = os.path.split(self.paper_file.name)
        return tail

    @property
    def paper_file_name(self):
        """compose paper short name. this name has the following format:
        year_first-author-surname_title
        """
        pub_year = self.publication_date.year if self.publication_date else ''
        if self.authors_info:
            author_surname = '_{}'.format(self.authors_info.first().author.name.title())
        else:
            author_surname = ''
        return '{y}{a}_{t}'.format(y=pub_year, a=author_surname, t=self.smart_title)

    @property
    def smart_title(self):
        smart_title = ''
        if self.title:
            # try to make it smart
            if '\n' in self.title:
                words_ret = smart_title.split('\n')
                smart_title = words_ret[0].strip()
            elif ':' in self.title:
                words_col = smart_title.split(':')
                smart_title = words_col[0].strip()
            elif '(' in self.title:
                words_p = smart_title.split('(')
                smart_title = words_p[0].strip()
            else:
                smart_title = self.title
        return smart_title

    @property
    def short_title(self):
        return self.authors_short

    @property
    def tags(self):
        return self.terms

    @property
    def preview(self):
        return self.abstract

    @property
    def authors_short(self):
        all_authors = self.authors_info.order_by('author_order')
        first_author = all_authors[0].author
        oths = '(et al.)' if all_authors.count() > 1 else ''
        y = self.publication_date.year if self.publication_date else ''
        return '{fa} {oths}, {year}'.format(fa=first_author.name,
                                            oths=oths, year=y)

    @property
    @mark_safe
    def resource_icon(self):
        return '<i class="fas fa-file-contract"></i>'

    @property
    @mark_safe
    def label(self):
        return '''
            <span class="badge badge-danger" style="float: right; position: relative;">
            <i class="fas fa-file-contract"></i>&nbsp;&nbsp;Paper
            </span>
            '''

    @property
    def resource_type(self):
        return 'paper'

    @property
    def border_css(self):
        return 'border-danger'

    @property
    def badge_css(self):
        return 'badge-danger'

    @property
    def most_popular_terms(self):
        tags = self.terms.annotate(np=models.Count('papers')).order_by('-np')
        return tags[:5]

    def authors_and_affiliations(self):
        authors_info = self.authors_info.order_by('author_order')
        affiliations_map = dict()
        authors_list = list()
        affiliation_counter = 1
        for info in authors_info:
            affiliations = info.affiliations.all()
            authors_affiliation_counters = list()
            for affiliation in affiliations:
                if not affiliation.name in affiliations_map:
                    affiliations_map[affiliation.name] = affiliation_counter
                    authors_affiliation_counters.append(affiliation_counter)
                    affiliation_counter += 1
                else:
                    counter = affiliations_map[affiliation.name]
                    authors_affiliation_counters.append(counter)
            authors_list.append({'author': info.author,
                                 'affiliations': authors_affiliation_counters})

        return (authors_list, affiliations_map)

    def delete(self, using=None, keep_parents=False):
        super(Paper, self).delete(using, keep_parents)
        if self.paper_file:
            try:
                resource_path = self.paper_file.file.name
                os.remove(resource_path)
            except FileNotFoundError:
                pass

    def __str__(self):
        return self.title

    def __repr__(self):
        return str(self)

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model),
                       args=(self.id,))

    def get_absolute_url(self):
        return reverse('paper_get', args=[str(self.reference_id)])

    class Meta:
        verbose_name = 'Paper'
        verbose_name_plural = 'Papers'
        get_latest_by = ['-last_change']


class AuthorPaper(models.Model):
    author = models.ForeignKey(Author, verbose_name='Author', related_name='paper_info',
                               on_delete=models.CASCADE)
    paper = models.ForeignKey(Paper, verbose_name='Paper', related_name='authors_info',
                              on_delete=models.CASCADE)
    author_order = models.PositiveSmallIntegerField(verbose_name='Author Order')

    affiliations = models.ManyToManyField('Affiliation', related_name='authors', blank=True)

    def __str__(self):
        return '{} as Author of {}'.format(str(self.author),
                                           str(self.paper))

    def __repr__(self):
        return str(self)

    class Meta:
        get_latest_by = "author_order"


class Affiliation(models.Model):
    # Affiliation Information
    name = models.CharField(max_length=300, verbose_name='Institution Name', unique=True,
                            help_text='Name of the Affiliation Institution')
    country = models.CharField(max_length=200, verbose_name='Institution Country',
                               null=True, blank=True,
                               help_text='(Optional) Country of Affiliation')
    city = models.CharField(max_length=200, verbose_name='Institution City',
                            null=True, blank=True,
                            help_text='(Optional) City of Affiliation')

    def __str__(self):
        return '{} ({}, {})'.format(self.name, self.city, self.country)

    def __repr__(self):
        return str(self)


# ================
# Dataset Section
# ================

class Dataset(models.Model):
    """Dataset"""

    full_name = models.CharField(verbose_name='Dataset Name', max_length=250,
                                 help_text='Full Name of the Resource')

    short_name = models.CharField(verbose_name='Short Name', max_length=40, unique=True,
                                  help_text='Short Mnemonic Name (UNIQUE)')

    description = MarkdownxField(verbose_name='Description',
                                 help_text='(Full) Description of the Resource')

    short_description = MarkdownxField(verbose_name='Short Description', blank=True, null=True,
                                       help_text='(Optional) Short Description of the Resource')

    # Sections about Statistics
    n_patients = models.PositiveIntegerField(verbose_name='Number of Patients in the Study', default=0)
    patients_in_study = models.CharField(max_length=3, choices=PATIENTS_CHOICES, blank=True,
                                         default='')
    release_year = models.PositiveIntegerField(verbose_name='Release Year', blank=True, null=True)
    web_url = models.URLField(verbose_name='Source URL')

    # Reference Paper
    reference_paper = models.ForeignKey(Paper, related_name='dataset',
                                        null=True, blank=True,
                                        verbose_name='Reference Paper',
                                        help_text='(Optional) Reference Paper: \
                                           The paper published along with the dataset',
                                        on_delete=models.SET_NULL)

    # Papers working on this dataset
    paper_references = models.ManyToManyField(Paper, through='ExperimentalStudy',
                                              related_name='experimental_data',
                                              through_fields=('dataset', 'paper'),
                                              verbose_name='Experimental Studies',
                                              help_text='(Optional) Papers using, mentioning, \
                                                        or referencing this dataset in their \
                                                        study or experiments.')

    # Tags
    tags = models.ManyToManyField(Keyword, related_name='datasets')
    pathology = models.ForeignKey(Pathology, verbose_name='Pathology', null=True,
                                  related_name='datasets', on_delete=models.SET_NULL)

    # Upload Statistics
    upload_date = models.DateField(editable=False, auto_now_add=True)
    last_change = models.DateTimeField(editable=False, auto_now=True)

    #Azure keys
    azure_keys = models.ManyToManyField(AzureKey, related_name='datasets', verbose_name='Azure Keys', blank=True)
    update_azure_keys = models.BooleanField(default=True, verbose_name='Update Azure keys')

    def __str__(self):
        return self.short_name

    def __repr__(self):
        return str(self)

    @property
    @mark_safe
    def resource_icon(self):
        return '<i class="fas fa-archive"></i>'

    @property
    @mark_safe
    def label(self):
        return '''
        <span class="badge badge-warning" style="float: right; position: relative;">
        <i class="fas fa-archive"></i> &nbsp;&nbsp;Dataset
        </span>
        '''

    @property
    def resource_type(self):
        return 'dataset'

    @property
    def border_css(self):
        return 'border-warning'

    @property
    def badge_css(self):
        return 'badge-warning'

    @property
    def title(self):
        return self.full_name

    @property
    def short_title(self):
        return self.short_name

    @property
    def preview(self):
        if self.short_description:
            return self.short_description
        return self.description

    @property
    def most_popular_tags(self):
        tags = self.tags.annotate(np=models.Count('datasets')).order_by('-np')
        return tags[:5]

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model),
                       args=(self.id,))

    def get_absolute_url(self):
        return reverse('dataset_get', args=[str(self.short_name.lower())])

    class Meta:
        verbose_name = 'Dataset'
        verbose_name_plural = 'Datasets'
        get_latest_by = ['-upload_change']


class DataArchive(models.Model):
    """Data Archive Resource associated to a Dataset"""

    dataset = models.ForeignKey(to=Dataset, related_name='data_archives',
                                on_delete=models.CASCADE)

    # Archive File
    archive_type = models.CharField(max_length=3, choices=DATA_TYPES_CHOICES)

    archive_format = models.CharField(max_length=200, verbose_name='Format',
                                      blank=True, default='',
                                      help_text='(Optional) Format/Extension of the data files')

    name = models.CharField(max_length=80, blank=True, default='',
                            verbose_name='Label',
                            help_text='(Optional) Label to associate to the data package')

    archive_file = ResumableFileField(verbose_name='Resource File',
                                      upload_to=archive_upload_path,
                                      max_length=500,
                                      chunks_upload_to='dataarchive_chunks/')

    notes = MarkdownxField(verbose_name='Notes', blank=True,
                           help_text='(Optional) Additional Notes')

    # Upload Statistics
    upload_date = models.DateField(editable=False, auto_now_add=True)
    last_change = models.DateTimeField(editable=False, auto_now=True)

    @property
    def label(self):
        format = '(of {})'.format(self.archive_format) if self.archive_format else ''
        label = '{name} {of}'.format(name=self.name if self.name else 'Package',
                                     of=format)
        return label

    def __str__(self):
        if self.name:
            return self.name
        return 'Data Attachment for {}'.format(self.dataset.short_name.upper())

    def __repr__(self):
        return str(self)

    def delete(self, using=None, keep_parents=False):
        try:
            resource_path = self.archive_file.file.name
            os.remove(resource_path)
        except FileNotFoundError:
            pass
        finally:
            super(DataArchive, self).delete(using, keep_parents)

    @property
    def filename(self):
        _, tail = os.path.split(self.archive_file.name)
        return tail

    class Meta:
        verbose_name = 'Attachment'
        verbose_name_plural = 'Attachments'
        get_latest_by = ['-upload_change']


class ExperimentalStudy(models.Model):
    """
    An `ExperimentalStudy` connects together Papers and Datasets.
    There is a connection between papers and datasets whether a paper
    uses the corresponding dataset in its experimental settings.
    This connections may go with short notes and names (mnemonic)
    for quick future reference and search.
    """

    paper = models.ForeignKey(Paper, related_name='experimental_study', on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, related_name='experimental_study', on_delete=models.CASCADE)
    method = models.ForeignKey(Method, verbose_name='Algorithm or Method', on_delete=models.CASCADE,
                               null=True, related_name='studies')

    name = models.CharField(max_length=100, verbose_name='Label', blank=True, null=True,
                            help_text='(Optional) Short name to identify the study')
    notes = MarkdownxField(verbose_name='Notes', blank=True, null=True, max_length=1000,
                           help_text='(Optional) Short description or notes about the experimental study')

    # Upload Statistics
    upload_date = models.DateField(editable=False, auto_now_add=True)
    last_change = models.DateTimeField(editable=False, auto_now=True)

    def __str__(self):
        return '{} on {}'.format(str(self.paper), str(self.dataset))

    @property
    def most_popular_terms(self):
        paper_terms = self.paper.terms.annotate(np=models.Count('papers'))
        dataset_tags = self.dataset.tags.annotate(nd=models.Count('datasets'))
        tags = [(t.np, t) for t in paper_terms]
        tags.extend([(t.nd, t) for t in dataset_tags])
        tags = [t[1] for t in sorted(tags, key=lambda t: t[0], reverse=True)]
        return tags[:5]

    @property
    @mark_safe
    def resource_icon(self):
        return '<i class="fas fa-flask"></i>'

    @property
    @mark_safe
    def label(self):
        return '''
               <span class="badge badge-dark" style="float: right; position: relative;">
               <i class="fas fa-flask"></i>&nbsp;&nbsp;Experimental Study
               </span>
               '''

    @property
    def badge_css(self):
        return 'badge-dark'

    @property
    def border_css(self):
        return 'border-dark'

    @property
    def resource_type(self):
        return 'study'

    @property
    @mark_safe
    def short_title(self):
        return '{} {}'.format(self.dataset.resource_icon, self.dataset.short_title.title())

    @property
    def title(self):
        return '{} {}'.format(self.paper.resource_icon, self.paper.title.title())

    @property
    def preview(self):
        return self.paper.preview

    @property
    def pathology(self):
        return self.paper.pathology

    @property
    def tags(self):
        return self.paper.tags

    def get_absolute_url(self):
        return reverse('study_get', args=[str(self.id)])

    class Meta:
        get_latest_by = ['-upload_change']
        verbose_name = 'Experimental Study'
        verbose_name_plural = 'Experimental Studies'


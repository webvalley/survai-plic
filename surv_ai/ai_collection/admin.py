from django.contrib import admin

from .models import Paper, AuthorPaper
from .models import Keyword, Method, AzureKey
from .models import Author
from .models import Dataset, DataArchive, Pathology, PathologyCategory
from .models import ExperimentalStudy
from .models import PATHOLOGY_CATEGORY_DEFAULT_DISPLAY
from .models import _display_badge
from .models import Topic

from django.conf import settings
from ai_collection.azure_api import get_azurekeys

from .forms import PaperCreationForm, PaperChangeForm
from .forms import BadgeClassForm
from django.contrib.admin.options import IS_POPUP_VAR

from markdownx.widgets import AdminMarkdownxWidget
from django.db import models
from django.utils.html import mark_safe


class ResourceTagAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['show_badge']
    form = BadgeClassForm
    fieldsets = (
        (None, {
            'fields': ('name', 'badge_class'),
            'classes': ('wide',),
        }),
    )

    @mark_safe
    def show_badge(self, obj):
        return obj.badge

    show_badge.short_description = 'Name'
    show_badge.admin_order_field = 'name'

    class Media:
        css = {
            'all': ('css/badges.min.css',)
        }
        js = ("js/badges.js",)


class AzureKeyAdmin(admin.ModelAdmin):

    change_list_template = 'ai_collection/admin/change_list.html'
    list_display = ['name','show_papers', 'show_datasets']
    search_fields = ['name']
    actions = ['delete_unused']

    def delete_unused(modeladmin, request, queryset):
        for key in queryset.all():
            if len(key.papers.all()) == 0 and len(key.datasets.all()) == 0:
                key.delete()
    delete_unused.short_description = 'Delete Azure Keyphrases with no paper nor dataset'

    @mark_safe
    def show_papers(self, azurekey):
        #papers = azurekey.papers.order_by('-publication_date')
        papers = azurekey.papers.all()
        n_papers = papers.count()

        tag = '''
                    <b>Total: </b> {count}
                    <br>
                    <ol>
                        {list_papers}
                    </ol>
                '''
        paper_entry = '<li><a href="{url}" title="{title}" target="_blank">{name}</a></li>'
        list_papers = ' '.join([paper_entry.format(url=p.get_admin_url(), title=p.title,
                                                   name='Paper: {n} ({y})'.format(y=p.publication_date.year,
                                                                                  n=p.smart_title))
                                for p in papers])
        return tag.format(count=n_papers,
                          list_papers=list_papers)

    show_papers.short_description = "Papers"

    @mark_safe
    def show_datasets(self, azurekey):
        # papers = azurekey.papers.order_by('-publication_date')
        datasets = azurekey.datasets.all()
        n_datasets = datasets.count()

        tag = '''
                        <b>Total: </b> {d_count}
                        <br>
                        <ol>
                            {list_datasets}
                        </ol>
                    '''
        paper_entry = '<li><a href="{url}" title="{title}" target="_blank">{name}</a></li>'
        list_datasets = ' '.join([paper_entry.format(url=p.get_admin_url(), title=p.short_name,
                                                   name='Dataset: {n} '.format(
                                                                                  n=p.short_name))
                                for p in datasets])
        return tag.format(d_count=n_datasets,
                          list_datasets=list_datasets)

    show_datasets.short_description = "Datasets"


class MethodAdmin(ResourceTagAdmin):
    """Admin class for Method model instances"""
    list_display = ['show_badge', 'show_studies']

    @mark_safe
    def show_studies(self, method):
        studies = method.studies.order_by('-paper__publication_date')
        n_studies = studies.count()
        tag = '''
            <b>Total: </b> {count}
            <br>
            <ol>
                {list_studies}
            </ol>
        '''
        entry = '''
            <li>
                <a href="{p_url}" title="{p_title}" target="_blank">{p_name}</a>
                on
                <a href="{ds_url}" title="{ds_name}" target="_blank">{ds_sname}</a>
            </li>
        '''
        list_study = ' '.join([entry.format(ds_url=s.dataset.get_admin_url(),
                                            ds_name=s.dataset.full_name,
                                            ds_sname=s.dataset.short_name,
                                            p_url=s.paper.get_admin_url(),
                                            p_title=s.paper.title,
                                            p_name='({y}) {t}'.format(y=s.paper.publication_date.year,
                                                                      t=s.paper.smart_title))
                                for s in studies])
        return tag.format(count=n_studies,
                          list_studies=list_study)

    show_studies.short_description = "Experimental Studies"


class KeywordAdmin(ResourceTagAdmin):
    """Admin class for Keyword model instances"""
    list_display = ['show_badge', 'show_papers', 'show_datasets']

    @mark_safe
    def show_papers(self, keyword):
        papers = keyword.papers.order_by('-publication_date')
        n_papers = papers.count()

        tag = '''
                <b>Total: </b> {count}
                <br>
                <ol>
                    {list_papers}
                </ol>
            '''
        paper_entry = '<li><a href="{url}" title="{title}" target="_blank">{name}</a></li>'
        list_papers = ' '.join([paper_entry.format(url=p.get_admin_url(), title=p.title,
                                                   name='Paper: {n} ({y})'.format(y=p.publication_date.year,
                                                                           n=p.smart_title))
                                for p in papers])
        return tag.format(count=n_papers,
                          list_papers=list_papers)

    show_papers.short_description = "Papers"

    @mark_safe
    def show_datasets(self, keyword):
        datasets = keyword.datasets.order_by('-release_year')
        n_datasets = datasets.count()
        tag = '''
                        <b>Total: </b> {count}
                        <br>
                        <ul>
                            {list_datasets}
                        </ul>
                    '''
        ds_entry = '<li><a href="{url}" title="{title}" target="_blank">{name}</a></li>'
        list_datasets = ' '.join([ds_entry.format(url=d.get_admin_url(), title=d.full_name,
                                                  name='Dataset {n} ({y})'.format(y=d.release_year,
                                                                          n=d.short_name))
                                  for d in datasets])
        return tag.format(count=n_datasets,
                          list_datasets=list_datasets)

    show_datasets.short_description = "Datasets"


class PathologyCategoryAdmin(ResourceTagAdmin):
    """Admin class for Keyword model instances"""
    list_display = ['show_badge', 'show_pathologies']

    @mark_safe
    def show_pathologies(self, keyword):
        pathologies = keyword.pathologies.all()
        n_pathologies = pathologies.count()

        tag = '''
                <b>Total: </b> {count}
                <br>
                <ol>
                    {list_pathologies}
                </ol>
            '''
        pathology_entry = '<li><a href="{url}" title="{title}" target="_blank">{name}</a></li>'
        list_pathologies = ' '.join([pathology_entry.format(url=p.get_admin_url(), title=str(p),
                                                       name='Pathology: {n}'.format(n=str(p)))
                                for p in pathologies])
        return tag.format(count=n_pathologies,
                          list_pathologies=list_pathologies)

    show_pathologies.short_description = "Pathologies"


class PathologyAdmin(ResourceTagAdmin):
    list_display = ['show_badge', 'show_pathology_category', 'show_papers', 'show_datasets']
    list_display_links = ['show_pathology_category', 'show_badge']
    list_filter = ['category', ]
    sortable_by = ['show_pathology_category', 'show_badge']
    autocomplete_fields = ['category']
    fieldsets = (
        (None, {
            'fields': ('name', 'badge_class', 'category'),
            'classes': ('wide',),
        }),
    )

    @mark_safe
    def show_pathology_category(self, pathology):
        return pathology.badge_category
    show_pathology_category.short_description = 'Pathology Category'
    show_pathology_category.admin_order_field = 'category'

    @mark_safe
    def show_papers(self, pathology):
        papers = pathology.papers.order_by('-publication_date')
        n_papers = papers.count()

        tag = '''
            <b>Total: </b> {count}
            <br>
            <ol>
                {list_papers}
            </ol>
        '''
        paper_entry = '<li><a href="{url}" title="{title}" target="_blank">{name}</a></li>'
        list_papers = ' '.join([paper_entry.format(url=p.get_admin_url(), title=p.title,
                                                   name='Paper: {n} ({y})'.format(y=p.year_of_publication,
                                                                           n=p.smart_title)
        )
                                for p in papers])
        return tag.format(count=n_papers,
                          list_papers=list_papers)
    show_papers.short_description = "Papers"

    @mark_safe
    def show_datasets(self, pathology):
        datasets = pathology.datasets.order_by('-release_year')
        n_datasets = datasets.count()
        tag = '''
                            <b>Total: </b> {count}
                            <br>
                            <ul>
                                {list_datasets}
                            </ul>
                        '''
        ds_entry = '<li><a href="{url}" title="{title}" target="_blank">{name}</a></li>'
        list_datasets = ' '.join([ds_entry.format(url=d.get_admin_url(), title=d.full_name,
                                                  name='Dataset {n} ({y})'.format(y=d.release_year,
                                                                                  n=d.short_name))
                                  for d in datasets])
        return tag.format(count=n_datasets,
                          list_datasets=list_datasets)

    show_datasets.short_description = "Datasets"


# ====================
# Papers Admin Section
# ====================

class InlineAuthorPaper(admin.StackedInline):
    model = AuthorPaper
    extra = 0
    filter_horizontal = ['affiliations', ]


class PaperAdmin(admin.ModelAdmin):
    # ChangeList view
    # ---------------
    change_list_template = 'ai_collection/admin/change_list.html'
    date_hierarchy = 'publication_date'
    list_display = ('title', 'show_pathology', 'show_pathology_category','Topic','show_paper_file')
    list_display_links = ('title',)
    list_filter = ('pathology__category', 'pathology', 'metadata_reference', 'terms','topic')
    list_select_related = ['pathology']
    search_fields = ('title', 'authors__name','azure_keys__name','topic__name')
    sortable_by = ['title', 'show_pathology', 'show_pathology_category']

    # Add/Change view
    # ---------------
    add_form_template = "ai_collection/admin/paper/add_form.html"
    add_form = PaperCreationForm
    form = PaperChangeForm
    inlines = [InlineAuthorPaper, ]
    fieldsets = (
        (None, {
            'fields': (  # ('reference_id', 'metadata_reference'),
                'title', 'abstract', 'paper_file'),
            'classes': ('wide',),

        }),

        ('Pathology & Terms', {
            'fields': ('pathology', 'terms','azure_keys','update_azure_keys','topic',),
        }),

        ('Publication Info', {
            'description': 'Editorial information of the published paper',
            'fields': ('venue', 'year_of_publication', 'paper_url',
                       'article_type', 'aggregation_type',
                       'volume', 'publication_date',
                       ('doi', 'issn', 'eid', 'pubmed_id'),
                       ),
            'classes': ('wide',),
        }),

    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('metadata_reference', 'reference_id'),
        }),
    )
    formfield_overrides = {
        models.TextField: {'widget': AdminMarkdownxWidget},
    }
    autocomplete_fields = ['terms', 'pathology','topic','azure_keys']

    @mark_safe
    def azure_keys_list(self,paper):
        return [k.name for k in paper.azure_keys.all()]

    def save_related(self, request,form, formsets, change):
        super(PaperAdmin, self).save_related(request, form, formsets, change)
        print(form.instance.azure_keys.all())
        try:
            if not form.instance.update_azure_keys:
                return
            keys = get_azurekeys(form.instance.abstract)
            print(keys)
            for key in keys:
                if len(key) >= 50:
                    continue
                key = key.lower()
                if len(AzureKey.objects.filter(name=key)) == 0:     #If it does not exist
                    k = AzureKey.objects.create(name=key)
                    k.save()
                    form.instance.azure_keys.add(k)
                else:                                               #If it does exist
                    if len(form.instance.azure_keys.filter(name=key)) == 0:          #If it is not in the keys
                        k = AzureKey.objects.get(name=key)
                        form.instance.azure_keys.add(k)
        except Exception as e:
            print(e)


    @mark_safe
    def show_paper_file(self, obj):
        if obj.paper_file:
            tag_link = '<a href="{url}" title="{title}" target="_blank">{name}</a>'
            return tag_link.format(url=obj.paper_file.url, title=obj.title,
                                   name='Open Paper File')
        else:
            return '<b>File is missing</b>'

    show_paper_file.short_description = 'Paper File'

    @mark_safe
    def Topic(self,paper):
        #return paper.topic.badge #_display_badge(paper.topic.badge_class,paper.topic.name.title())
        if paper.topic:
            return paper.topic.badge
        return _display_badge(color_class='badge-secondary', text='No Topic')


    @mark_safe
    def show_terms(self, obj):
        terms = obj.terms.all()
        if terms.count() == 0:
            return 'No Term for this Paper'
        return '<br>'.join([t.badge for t in terms])

    show_terms.short_description = 'Keywords'
    show_terms.admin_order_field = 'terms'

    @mark_safe
    def show_pathology(self, paper):
        if paper.pathology:
            return paper.pathology.badge
        return _display_badge(color_class='badge-secondary', text='No Pathology')

    show_pathology.short_description = 'Pathology'
    show_pathology.admin_order_field = 'pathology'

    @mark_safe
    def show_pathology_category(self, paper):
        if paper.pathology is None:
            return _display_badge(text=PATHOLOGY_CATEGORY_DEFAULT_DISPLAY, color_class='badge-secondary')
        else:
            return paper.pathology.badge_category

    show_pathology_category.short_description = 'Pathology Category'
    show_pathology_category.admin_order_field = 'pathology__category'

    # =======================
    # Add/Change View Methods
    # =======================

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def save_form(self, request, form, change):
        if not change:
            # this is the case of form add. So, go ahead with
            # Metadata download from engine
            if form.crawler is not None:
                form.crawler.crawl_paper(paper_instance=form.instance)
            return form.save(commit=False)
        return super().save_form(request, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        """
        Determine the HttpResponse for the add_view stage. It mostly defers to
        its superclass implementation but is customized because the User model
        has a slightly different workflow.
        """
        # We should allow further modification of the user just added i.e. the
        # 'Save' button should behave like the 'Save and continue editing'
        # button except in two scenarios:
        # * The user has pressed the 'Save and add another' button
        # * We are adding a user in a popup
        if '_addanother' not in request.POST and IS_POPUP_VAR not in request.POST:
            request.POST = request.POST.copy()
            request.POST['_continue'] = 1
        return super().response_add(request, obj, post_url_continue)

    class Media:
        css = {
            'all': ('css/badges.css',)
        }


class AuthorAdmin(admin.ModelAdmin):
    """Admin Manager for Author model instances"""

    change_list_template = 'ai_collection/admin/change_list.html'
    list_display = ('name', 'indexed_name', 'show_papers')
    search_fields = ('name',)

    # ------------------
    # Changelist Methods
    # ------------------

    @staticmethod
    def ordinal(n):
        return "%d%s" % (n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])

    @mark_safe
    def show_papers(self, author):
        """"""
        author_papers = author.paper_info.order_by('-paper__publication_date',
                                                   'author_order')
        n_papers = author_papers.count()
        tag = '''
            <b>Total: </a> {count}
            <ol>
                {list_papers}
            </ol>
        '''
        paper_entry = '<li><a href="{url}" title="{title}" target="_blank">{name}</a></li>'
        list_papers = ' '.join([paper_entry.format(url=ap.paper.get_admin_url(), title=ap.paper.title,
                                                   name='{t} (as {o} author)'.format(
                                                       o=self.ordinal(ap.author_order),
                                                       t=ap.paper.smart_title
                                                    ))
                                for ap in author_papers])

        return tag.format(count=n_papers, list_papers=list_papers)

    show_papers.short_description = 'Authored Papers'


# class AffiliationAdmin(admin.ModelAdmin):
#     list_display = ('name', 'city', 'country', 'display_authors_count')
#     search_fields = ('name', 'city')
#
#     def display_authors_count(self, obj):
#         return 'Related Authors: {}'.format(obj.authors.count())


# =====================
# Dataset Admin Section
# =====================


class DataInlineAdmin(admin.StackedInline):
    model = DataArchive
    extra = 1

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'archive_type', 'archive_format',
                'archive_file'),
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

class ExperimentalStudyInlineAdmin(admin.StackedInline):
    model = ExperimentalStudy
    extra = 1
    autocomplete_fields = ['method']

    fieldsets = (
        (None, {
            'fields': ('paper', 'method'),
            'classes': ('wide',)
        }),
        ('Additional Information', {
            'fields': ('name', 'notes'),
            'classes': ('collapse',)
        }),
    )

class TopicAdmin(ResourceTagAdmin):
    list_display = ['show_badge','show_papers']
    list_display_links = ['show_badge']
    #list_filter = ['category', ]
    sortable_by = ['show_badge']
    #autocomplete_fields = ['category']
    fieldsets = (
        (None, {
            'fields': ('name', 'badge_class'),   #'category'
            'classes': ('wide',),
        }),
    )

   # @mark_safe
   # def show_pathology_category(self, pathology):
   #     return pathology.badge_category
   # show_pathology_category.short_description = 'Pathology Category'
   # show_pathology_category.admin_order_field = 'category'

    @mark_safe
    def show_papers(self, pathology):
        papers = pathology.papers.order_by('-publication_date')
        n_papers = papers.count()

        tag = '''
            <b>Total: </b> {count}
            <br>
            <ol>
                {list_papers}
            </ol>
        '''
        paper_entry = '<li><a href="{url}" title="{title}" target="_blank">{name}</a></li>'
        list_papers = ' '.join([paper_entry.format(url=p.get_admin_url(), title=p.title,
                                                   name='Paper: {n} ({y})'.format(y=p.year_of_publication,
                                                                           n=p.smart_title)
        )
                                for p in papers])
        return tag.format(count=n_papers,
                          list_papers=list_papers)
    show_papers.short_description = "Papers"

    @mark_safe
    def show_datasets(self, pathology):
        datasets = pathology.datasets.order_by('-release_year')
        n_datasets = datasets.count()
        tag = '''
                            <b>Total: </b> {count}
                            <br>
                            <ul>
                                {list_datasets}
                            </ul>
                        '''
        ds_entry = '<li><a href="{url}" title="{title}" target="_blank">{name}</a></li>'
        list_datasets = ' '.join([ds_entry.format(url=d.get_admin_url(), title=d.full_name,
                                                  name='Dataset {n} ({y})'.format(y=d.release_year,
                                                                                  n=d.short_name))
                                  for d in datasets])
        return tag.format(count=n_datasets,
                          list_datasets=list_datasets)

    show_datasets.short_description = "Datasets"


class DatasetAdmin(admin.ModelAdmin):
    """Admin Manager class for Dataset model"""
    change_list_template = 'ai_collection/admin/change_list.html'
    list_display = ['short_name',
                    'show_pathology', 'show_pathology_category',
                    'show_patients', 'show_reference_paper',
                    'show_attachments', 'show_experimental_study', 'show_web_url']
    inlines = [DataInlineAdmin, ExperimentalStudyInlineAdmin]
    list_filter = ['release_year', 'pathology__category', 'pathology', 'patients_in_study', 'tags', ]
    sortable_by = ['short_name', 'show_pathology', 'show_pathology_category', 'show_patients']
    search_fields = ('short_name', 'full_name','azure_keys__name')
    autocomplete_fields = ['tags', 'pathology','azure_keys']

    fieldsets = (
        (None, {
            'fields': (('full_name', 'short_name'),),
            'classes': ('wide',)
        }),

        ('Stats & References', {
            # 'classes': ('wide',),
            'fields': (('n_patients', 'patients_in_study',),
                       ('web_url', 'release_year',),
                       'reference_paper'),

        }),
        ('Description', {
            'classes': ('wide', 'collapse'),
            'fields': ('description',),

        }),
        ('Short Description', {
            'classes': ('wide', 'collapse'),
            'fields': ('short_description',),

        }),
        ('Metadata', {
            'fields': ('pathology', 'tags','azure_keys','update_azure_keys'),
        }),

    )

    formfield_overrides = {
        models.TextField: {'widget': AdminMarkdownxWidget},
    }

    # ============================
    # ChangeList (Display) Methods
    # ============================

    def azure_keys_list():
        return [k.name for k in azure_keys.all()]

    def save_related(self, request, form, formsets, change):
        super(DatasetAdmin, self).save_related(request, form, formsets, change)
        if not form.instance.update_azure_keys:
            return
        try:
            form.instance.azure_keys.set(form.instance.reference_paper.azure_keys.all())
        except Exception as e:
            print(e)

        #print(form.instance.azure_keys.all())
        #try:
        #    if not form.instance.update_azure_keys:
        #        return
        #    keys = get_azurekeys(form.instance.reference_paper.abstract)
        #    print(keys)
        #    for key in keys:
        #        key = key.lower()
        #        if len(AzureKey.objects.filter(name=key)) == 0:     #If it does not exist
        #            k = AzureKey.objects.create(name=key)
        #            k.save()
        #            form.instance.azure_keys.add(k)
        #        else:                                               #If it does exist
        #            if len(form.instance.azure_keys.filter(name=key)) == 0:          #If it is not in the keys
        #                k = AzureKey.objects.get(name=key)
        #                form.instance.azure_keys.add(k)
        #except Exception as e:
        #    print(e)

    @mark_safe
    def show_attachments(self, obj):
        tag = '''
            <b>Attachments: </b> {count}
            <br>
            <ul>
                {list_tag}
            </ul>
        '''
        list_item_tag = '<li><span>{name}:</span> <a href="{url}" title="{name}" target="_blank">{label}</a></li>'
        archives = obj.data_archives.all()
        attachments = ' '.join([list_item_tag.format(name=a.label, url=a.archive_file.url,
                                                     label='Download') for a in archives])
        return tag.format(list_tag=attachments, count=archives.count())

    show_attachments.short_description = 'Attachments'

    @mark_safe
    def show_reference_paper(self, obj):
        if obj.reference_paper:
            tag_link = '<a href="{url}" title="{title}" target="_blank">{name}</a>'
            return tag_link.format(url=obj.reference_paper.get_admin_url(),
                                   title=obj.reference_paper.smart_title,
                                   name='Open')
        else:
            return '<b>No Reference Paper</b>'

    show_reference_paper.short_description = 'Reference Paper'

    @mark_safe
    def show_web_url(self, obj):
        tag = '<a href="{url}" title="{title}" target="_blank" >{name}</a>'.format(
            url=obj.web_url, title=obj.full_name, name="Open")
        return tag

    show_web_url.short_description = 'Web URL'

    @mark_safe
    def show_pathology(self, dataset):
        if dataset.pathology:
            return dataset.pathology.badge
        return _display_badge(color_class='badge-secondary', text='No Pathology')

    show_pathology.short_description = 'Pathology'
    show_pathology.admin_order_field = 'pathology'

    @mark_safe
    def show_pathology_category(self, dataset):
        if dataset.pathology is None:
            return _display_badge(text=PATHOLOGY_CATEGORY_DEFAULT_DISPLAY, color_class='badge-secondary')
        else:
            return dataset.pathology.badge_category

    show_pathology_category.short_description = 'Pathology Category'
    show_pathology_category.admin_order_field = 'pathology__category'

    @mark_safe
    def show_experimental_study(self, obj):
        tag = '''
                    <b>Experimental Studies: </b> {count}
                    <br>
                    {methods_block}
                '''

        method_paper_list = '''
            <ul>
                {list_tag}
            </ul>
        '''

        different_methods = obj.experimental_study.values_list('method', flat=True)
        different_methods = set([method for method in different_methods])
        methods_block = '<br>'
        for method_name in sorted(different_methods):
            studies = obj.experimental_study.filter(method__name__iexact=method_name)
            list_item_tag = '<li> <a href="{url}" title="{title}" target="_blank">{label}</a>' \
                            '</li>'
            attachments = ' '.join([list_item_tag.format(url=es.paper.get_admin_url(),
                                                         title=es.paper.title,
                                                         label='Paper') for es in studies])
            block = method_paper_list.format(list_tag=attachments)
            method = Method.objects.get(name=method_name)
            methods_block += '{method}</br>{block}'.format(method=method.badge, block=block)

        studies_count = obj.experimental_study.count()
        return tag.format(count=studies_count, methods_block=methods_block)

    show_experimental_study.short_description = 'Experimental Studies'

    @mark_safe
    def show_patients(self, obj):
        if obj.n_patients > 0:
            return '''
                <b>Total:</b> {number}
                <br>
                <span>({conf})</span>
            '''.format(number=obj.n_patients, conf=obj.get_patients_in_study_display())
        return '<b>Not Specified</b>'

    show_patients.short_description = 'Patients in the Dataset'
    show_patients.admin_order_field = 'n_patients'

    class Media:
        css = {
            'all': ('css/badges.css',)
        }


admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.index_title = settings.ADMIN_INDEX_TITLE
admin.site.site_header = settings.ADMIN_SITE_HEADER

# Badge-Classes
admin.site.register(Keyword, KeywordAdmin)
admin.site.register(Method, MethodAdmin)
admin.site.register(Pathology, PathologyAdmin)
admin.site.register(PathologyCategory, PathologyCategoryAdmin)

# Papers
admin.site.register(Paper, PaperAdmin)
admin.site.register(Author, AuthorAdmin)

# Dataset
admin.site.register(Dataset, DatasetAdmin)

#Topic
admin.site.register(Topic, TopicAdmin)

admin.site.register(AzureKey, AzureKeyAdmin)

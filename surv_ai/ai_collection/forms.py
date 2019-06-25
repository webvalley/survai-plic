from django import forms
from .models import Paper
from .models import (ARXIV_ENGINE, SCOPUS_ENGINE, SEMANTIC_SCHOLAR_ENGINE,
                     MANUAL_ENTRY, DEFAULT_MANUAL_PAPER_ENTRY)
from django.core.exceptions import ValidationError
from .crawlers import PaperIDNotFoundError, ArticleMetadataError, instantiate_crawler


# =================================
# Admin Backend Model Forms classes
# =================================

class PaperChangeForm(forms.ModelForm):
    class Meta:
        model = Paper
        fields = '__all__'


class PaperCreationForm(forms.ModelForm):
    error_messages = {
        ARXIV_ENGINE: "The ArXiv ID of the paper is not valid",
        SCOPUS_ENGINE: "The DOI of the paper is not valid",
        SEMANTIC_SCHOLAR_ENGINE: 'The Semantic Scholar ID of the paper is not valid',
        'paper_existing': "Another Paper with the same reference_id is already in the Archive"
    }

    reference_id = forms.CharField(max_length=200, required=False, label='ID',
                                   help_text='Unique ID for the Paper (i.e. DOI, Semantic Scholar ID, or ArxivID)')

    def __init__(self, *args, **kwargs):
        super(PaperCreationForm, self).__init__(*args, **kwargs)
        self._crawler = None
        self._paper_metadata = None

    @property
    def crawler(self):
        if self.is_valid():
            if not self._crawler:
                try:
                    crawler = instantiate_crawler(self.cleaned_data['reference_id'],
                                                  self.cleaned_data['metadata_reference'])
                except:
                    return None
                else:
                    self._crawler = crawler
            return self._crawler
        return None

    @property
    def paper_metadata(self):
        if self.is_valid():
            if not self._paper_metadata:
                self._paper_metadata = self.crawler.retrieve_paper_metadata()
            return self._paper_metadata
        return None

    def clean_reference_id(self):
        engine = self.cleaned_data.get('metadata_reference')
        paper_id = self.cleaned_data.get('reference_id')
        if not engine == MANUAL_ENTRY:
            paper_id = paper_id.strip()
            is_valid = self.crawler.validate(paper_id=paper_id.strip())
            if not is_valid:
                raise ValidationError(self.error_messages.get(engine))
            return paper_id
        else:  # MANUAL_ENTRY
            paper_id_manual = '{}-{}'.format(DEFAULT_MANUAL_PAPER_ENTRY, 1)
            try:
                _ = Paper.objects.get(reference_id=paper_id_manual)
            except Paper.DoesNotExist:
                self.cleaned_data['reference_id'] = paper_id_manual
                return paper_id_manual
            else:
                manual_papers_ids = Paper.objects.filter(reference_id__startswith=
                                                         DEFAULT_MANUAL_PAPER_ENTRY).values_list('reference_id',
                                                                                                 flat=True)
                sorted_papers_ids = sorted(manual_papers_ids, key=lambda v: int(v.split('-')[1].strip()), reverse=True)
                latest_manual_count = int(sorted_papers_ids[0].split('-')[1].strip())
                paper_id = '{}-{}'.format(DEFAULT_MANUAL_PAPER_ENTRY, latest_manual_count+1)
                self.cleaned_data['reference_id'] = paper_id
                return paper_id

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        engine = self.cleaned_data.get('metadata_reference')
        reference_id = self.cleaned_data.get('reference_id')
        if reference_id and reference_id != DEFAULT_MANUAL_PAPER_ENTRY:
            try:
                _ = Paper.objects.get(reference_id=reference_id)
            except Paper.DoesNotExist:
                engine = self.cleaned_data['metadata_reference']
                if not engine == MANUAL_ENTRY:
                    try:
                        crawler = self.crawler
                        if crawler is not None:
                            self._paper_metadata = crawler.retrieve_paper_metadata()
                    except (PaperIDNotFoundError, ArticleMetadataError) as e:
                        self.add_error('reference_id', ValueError(str(e)))
            else:
                self.add_error('reference_id',
                               ValueError(self.error_messages['paper_existing']))

    class Meta:
        model = Paper
        fields = ("metadata_reference",
                  "reference_id")


class BadgeClassForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BadgeClassForm, self).__init__(*args, **kwargs)
        if self.instance:  # and self.instance.id:
            self.fields['badge_class'].choices = self.instance.badge_choices()
            self.fields['badge_class'].widget.attrs.update({'checked': 'checked'})

    class Meta:
        widgets = {
            'badge_class': forms.RadioSelect()
        }
        fields = '__all__'

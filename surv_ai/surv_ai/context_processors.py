
from django.conf import settings

def app_metadata(request):
    metadata = {'index_title': settings.INDEX_TITLE,
                'index_subtitle': settings.INDEX_SUBTITLE}
    if settings.INDEX_ALT_LOGO_PATH:
        metadata['index_alt_logo_path'] = settings.INDEX_ALT_LOGO_PATH
    if settings.INDEX_ALT_LOGO_TEXT:
        metadata['index_alt_logo_text'] = settings.INDEX_ALT_LOGO_TEXT
    return metadata
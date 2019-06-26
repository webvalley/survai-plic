# Copyright (c) 2019 Valerio Maggio <vmaggio@fbk.eu>
# Copyright (c) 2019 Marco Marinello <marco.marinello@school.rainerum.it>

from django.conf import settings

def app_metadata(request):
    metadata = {'index_title': settings.INDEX_TITLE,
                'index_subtitle': settings.INDEX_SUBTITLE}
    if settings.INDEX_ALT_LOGO_PATH:
        metadata['index_alt_logo_path'] = settings.INDEX_ALT_LOGO_PATH
    if settings.INDEX_ALT_LOGO_TEXT:
        metadata['index_alt_logo_text'] = settings.INDEX_ALT_LOGO_TEXT
    return metadata


def site_title(request):
    ctx = dict()
    if hasattr(settings, "ADMIN_SITE_TITLE"):
        ctx["ADMIN_SITE_TITLE"] = settings.ADMIN_SITE_TITLE
    return ctx

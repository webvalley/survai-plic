from django.urls import path
from .views import (papers_collection,
                    dataset_collection,
                    tags_collection,
                    pathologies_collection,
                    methods_collection,
                    paper_info, dataset_info,
                    resources_per_tag,
                    resources_per_pathology,
                    resources_per_pathology_category,
                    study_per_method, study_info,
                    index, studies_collection,
                    )

urlpatterns = [
    path('', index, name='index'),

    # Datasets
    path('datasets/<str:short_name>/',
         dataset_info, name='dataset_get'),
    path('datasets/', dataset_collection,
         name='datasets_all'),

    # Papers
    path('papers/<path:reference_id>/',
         paper_info, name='paper_get'),
    path('papers/', papers_collection,
         name='papers_all'),

    # Study
    path('studies/<int:study_id>/',
         study_info, name='study_get'),
    path('studies/',
         studies_collection, name='studies_all'),

    # Tag
    path('tags/<str:name>/', resources_per_tag,
         name='tag_resources'),
    path('tags/', tags_collection,
         name='tags_all'),  # Use List with counters

    # Pathology
    path('pathologies/<str:name>/', resources_per_pathology,
         name='pathology_resources'),
    path('pathologies-category/<str:name>/', resources_per_pathology_category,
         name='pathology_category_resources'),
    path('pathologies/', pathologies_collection,
         name='pathologies_all'),  # Use list with counters

    # Method
    path('methods/<str:name>/', study_per_method,
         name='method_studies'),
    path('methods/', methods_collection,
         name='methods_all'),  # use list with counters

]

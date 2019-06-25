from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from itertools import chain
from .models import Paper, Dataset, ExperimentalStudy
from .models import Keyword, Method, Pathology


def index(request):
    datasets = Dataset.objects.all()
    papers = Paper.objects.all()
    methods = Method.objects.all()
    pathologies = Pathology.objects.all()
    studies = ExperimentalStudy.objects.all()
    tags = Keyword.objects.all()

    context = {'papers_count': papers.count(),
               'datasets_count': datasets.count(),
               'studies_count': studies.count(),
               'algorithms_count': methods.count(),
               'pathologies_count': pathologies.count(),
               'tags_count': tags.count()}

    # --- Top
    # Latest (top 5) Papers
    top_papers = papers.order_by('-upload_date')[:5]
    # latest (top 5) Datasets
    top_datasets = datasets.order_by('-upload_date')[:5]
    # latest (top 5) Experimental Studies
    top_studies = studies.order_by('-upload_date')[:5]

    context.update({'latest_papers': top_papers,
                    'latest_datasets': top_datasets,
                    'latest_studies': top_studies})

    # --- Pathologies
    p_stats = Pathology.objects.all().annotate(np=Count('papers'),
                                               nd=Count('datasets'))
    top_paths = sorted(p_stats, key=lambda p: p.np + p.nd, reverse=True)[:10]

    # --- Algorithms
    a_stats = Method.objects.all().annotate(np=Count('studies__paper'),
                                            nd=Count('studies__dataset'))
    top_algos = sorted(a_stats, key=lambda a: a.np + a.nd, reverse=True)[:10]

    # --- Tags
    t_stats = Keyword.objects.all().annotate(np=Count('papers'),
                                             nd=Count('datasets'))
    # Most Used Tags (Top 3)
    top_kw_abs = sorted(t_stats, key=lambda t: t.np + t.nd, reverse=True)[:3]
    # Most Used Tags in Papers (Top 3)
    top_kw_papers = sorted(t_stats, key=lambda t: t.np, reverse=True)[:3]
    # Most Used Tags in Datasets (Top 3)
    top_kw_dsets = sorted(t_stats, key=lambda t: t.nd, reverse=True)[:3]

    context.update({'top_pathologies': top_paths,
                    'top_methods': top_algos,
                    'top_tags_all': top_kw_abs,
                    'top_tags_papers': top_kw_papers,
                    'top_tags_datasets': top_kw_dsets})

    return render(request, 'ai_collection/index.html', context)


def papers_collection(request):
    papers_collection = Paper.objects.all()
    context = {'resources': papers_collection,
               'collection_name': "Papers", }
    return render(request, 'ai_collection/collections.html', context)


def dataset_collection(request):
    dataset_collection = Dataset.objects.all()
    context = {'resources': dataset_collection,
               'collection_name': "Datasets", }
    return render(request, 'ai_collection/collections.html', context)


def dataset_info(request, short_name):
    dataset = get_object_or_404(Dataset, short_name__iexact=short_name)
    context = {'dataset': dataset,
               'collection_name': "Datasets",
               'reverse_view_name': 'datasets_all',
               }
    return render(request, 'ai_collection/dataset.html', context)


def paper_info(request, reference_id):
    paper = get_object_or_404(Paper, reference_id=reference_id)
    context = {'paper': paper,
               'collection_name': "Papers",
               'reverse_view_name': 'papers_all',
               }
    return render(request, 'ai_collection/paper.html', context)


def resources_per_tag(request, name):
    tag = get_object_or_404(Keyword, name=name)
    papers_collection = tag.papers.all()
    dataset_collection = tag.datasets.all()
    paper_count = papers_collection.count()
    dataset_count = dataset_collection.count()
    context = {'resources': list(chain(dataset_collection, papers_collection)),
               'tag_name': tag.name,
               'collection_name': "Tags",
               'reverse_view_name': 'tags_all',
               'paper_count': paper_count,
               'dataset_count': dataset_count}

    return render(request, 'ai_collection/resources_per_tag.html',
                  context)


def resources_per_pathology_category(request, name):
    papers_collection = Paper.objects.filter(pathology__category__name=name)
    dataset_collection = Dataset.objects.filter(pathology__category__name=name)
    tag_name = ''
    paper_count = papers_collection.count()
    dataset_count = dataset_collection.count()
    collection = list(chain(dataset_collection, papers_collection))
    tag_name = str(collection[0].pathology.category)
    context = {'resources': collection,
               'tag_name': tag_name,
               'collection_name': "Pathologies",
               'reverse_view_name': 'pathologies_all',
               'paper_count': paper_count,
               'dataset_count': dataset_count}
    return render(request, 'ai_collection/resources_per_tag.html',
                  context)


def resources_per_pathology(request, name, category=False):
    if not category:
        pathology = get_object_or_404(Pathology, name=name)
        papers_collection = pathology.papers.all()
        dataset_collection = pathology.datasets.all()
        tag_name = pathology.name
    else:
        papers_collection = Paper.objects.filter(pathology__category=name)
        dataset_collection = Dataset.objects.filter(pathology__category=name)
        tag_name = ''
    paper_count = papers_collection.count()
    dataset_count = dataset_collection.count()
    collection = list(chain(dataset_collection, papers_collection))
    if not tag_name:
        tag_name = str(collection[0].pathology.category)
    context = {'resources': collection,
               'tag_name': tag_name,
               'collection_name': "Pathologies",
               'reverse_view_name': 'pathologies_all',
               'paper_count': paper_count,
               'dataset_count': dataset_count}

    return render(request, 'ai_collection/resources_per_tag.html',
                  context)


def study_per_method(request, name):
    method = get_object_or_404(Method, name=name)
    collection = method.studies.order_by('dataset__short_name')
    tag_name = method.name
    paper_count = method.studies.distinct('paper__title').count()
    dataset_count = method.studies.distinct('dataset__short_name').count()
    context = {'resources': collection,
               'tag_name': tag_name,
               'collection_name': "Methods",
               'reverse_view_name': 'methods_all',
               'paper_count': paper_count,
               'dataset_count': dataset_count}

    return render(request, 'ai_collection/resources_per_tag.html',
                  context)


def study_on_dataset(request, short_name):
    dataset = get_object_or_404(Dataset, short_name=short_name)
    papers = dataset.paper_references.all()
    context = {'papers': papers}
    return render(request, 'ai_collection/')


def study_info(request, study_id):
    study = get_object_or_404(ExperimentalStudy, id=study_id)
    context = {'study': study,
               'collection_name': "Studies",
               'reverse_view_name': 'studies_all',
               }
    return render(request, 'ai_collection/study.html', context)


def studies_collection(request):
    studies_collection = ExperimentalStudy.objects.all()
    context = {'resources': studies_collection,
               'collection_name': "Studies", }
    return render(request, 'ai_collection/collections.html', context)


# Resources Collection (Keyword, Pathologies, Methods)

def tags_collection(request):
    tags = Keyword.objects.all()
    context = {'collection': tags,
               'collection_name': "Tags", }
    return render(request, 'ai_collection/tags.html', context)


def pathologies_collection(request):
    pathologies = Pathology.objects.all()
    context = {'collection': pathologies,
               'collection_name': "Pathologies", }
    return render(request, 'ai_collection/tags.html', context)


def methods_collection(request):
    methods = Method.objects.all()
    context = {'collection': methods,
               'collection_name': "Methods", }
    return render(request, 'ai_collection/tags.html', context)

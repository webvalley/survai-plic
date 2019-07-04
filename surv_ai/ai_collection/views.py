from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from itertools import chain
from .models import Paper, Dataset, ExperimentalStudy
from .models import Keyword, Method, Pathology, Topic


def index(request):
    datasets = Dataset.objects.all()
    papers = Paper.objects.all()
    methods = Method.objects.all()
    pathologies = Pathology.objects.all()
    studies = ExperimentalStudy.objects.all()
    tags = Keyword.objects.all()
    topics = Topic.objects.all()

    print(topics.count())
    context = {'papers_count': papers.count(),
               'datasets_count': datasets.count(),
               'studies_count': studies.count(),
               'algorithms_count': methods.count(),
               'pathologies_count': pathologies.count(),
               'tags_count': tags.count(),
               'topics_count': topics.count()}

    # --- Top
    # Latest (top 5) Papers
    top_papers = papers.order_by('-upload_date')[:5]
    # latest (top 5) Datasets
    top_datasets = datasets.order_by('-upload_date')[:5]
    # latest (top 5) Experimental Studies
    top_studies = studies.order_by('-upload_date')[:5]
    # latest (top 5) Topics
    top_topics = topics.order_by('-upload_date')[:5]

    context.update({'latest_papers': top_papers,
                    'latest_datasets': top_datasets,
                    'latest_studies': top_studies,
                    'latest_topics': top_topics})

    #---Topics
    topic_stats = Topic.objects.all().annotate(np=Count('papers'))
    top_topics2 = sorted(topic_stats, key=lambda topic: topic.np, reverse=True)[:10]
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
                    'top_topics': top_topics2,
                    'top_tags_all': top_kw_abs,
                    'top_tags_papers': top_kw_papers,
                    'top_tags_datasets': top_kw_dsets})

    return render(request, 'ai_collection/index.html', context)


def papers_collection(request):
    query = request.GET.get('q','')
    if query == '':
        result = Paper.objects.all()
    else:
        q1 = Paper.objects.filter(title__contains=query)
        q2 = Paper.objects.filter(authors__name__contains=query)
        q3 = Paper.objects.filter(azure_keys__name__contains=query)
        q4 = Paper.objects.filter(terms__name__contains=query)
        q5 = Paper.objects.filter(topic__name__contains=query)
        result = set(list(chain(q1,q2,q3,q4,q5)))

    context = {'resources': result,
               'collection_name': "Papers", }
    return render(request, 'ai_collection/collections.html', context)


def dataset_collection(request):
    query = request.GET.get('q', '')
    if query == '':
        result = Dataset.objects.all()
    else:
        q1 = Dataset.objects.filter(full_name__contains=query)
        q2 = Dataset.objects.filter(azure_keys__name__contains=query)
        q3 = Dataset.objects.filter(tags__name__contains=query)
        q4 = Dataset.objects.filter(short_name__contains=query)
        result = set(list(chain(q1,q2, q3,q4)))

    context = {'resources': result,
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
    query = request.GET.get('q', '')
    if query == '':
        result = ExperimentalStudy.objects.all()
    else:
        q1 = ExperimentalStudy.objects.filter(paper__title__contains=query)
        q2 = ExperimentalStudy.objects.filter(dataset__full_name__contains=query)
        q3 = ExperimentalStudy.objects.filter(method__name__contains=query)
        q4 = ExperimentalStudy.objects.filter(name__contains=query)
        result = set(list(chain(q1, q2, q3, q4)))

    context = {'resources': result,
               'collection_name': "ExperimentalStudy", }
    return render(request, 'ai_collection/collections.html', context)


def dataset_info(request, short_name):
    dataset = get_object_or_404(Dataset, short_name__iexact=short_name)
    context = {'dataset': dataset,
               'collection_name': "Datasets",
               'reverse_view_name': 'datasets_all',
               }
    return render(request, 'ai_collection/dataset.html', context)


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

def topics_collection(request):
    topics = Topic.objects.all()
    context = {'collection': topics,
               'collection_name': "Topics", }
    return render(request, 'ai_collection/topics_all.html', context)

def paper_per_topic(request,name):
    topic = get_object_or_404(Topic, name=name)
    papers_collection = topic.papers.all()
    tag_name = topic.name

    paper_count = papers_collection.count()
    collection = list(papers_collection)
    context = {'resources': collection,
               'tag_name': tag_name,
               'collection_name': "Topics",
               'reverse_view_name': 'topics_all',
               'paper_count': paper_count}

    return render(request, 'ai_collection/paper_per_topic.html',
                  context)

# SurvAI: Platform for AI Research Survey in Healthcare

This project provides a system that allows to collect, tag, and
navigate resources for AI in Healthcare.

Ultimately, the goal of the project is to create a curated collection of papers and
dataset related of Machine/Deep Learning for Health.

## Data Infrastructure

In terms of _Data Architecture_, the collection of resources is based on three main pillars:
`Paper`, `Dataset`, `ExperimentalStudy`.

- A `Paper` represent a publication available in the literature. Each `Paper` is uniquely identified
by a `doi`, and `arxivID`, or a `SemanticScholarID`. For this reason, the platform includes an integration
(whenever available) with **Scopus**, **Arxiv**, and **SemanticScholar** engines for automatic metadata acquisition.
Authors and their corresponding affiliations will be also managed.

- A `Dataset` embeds **data** and **metadata** of a dataset publicly available online, or
published in the literature. In terms of metadata, the platform allows to specify, for example,
how many patients are included in the dataset, what is the format of the available data,
the year of publication of the dataset, any public reference URL or a reference "Data Publication" `Paper`.
Moreover, the platform embeds an engine for the progressive upload of _large files_.

- An `ExperimentalStudy` connects a `Paper` to a `Dataset` through a `Method`. This entity in the database
serves the purpose to clarify which paper uses or leverages what dataset in their experimental studies,
by using or defining specific algorithm or techniques (e.g. `RandomForest` or `VGG` network).
The more the methods, the more the `ExperimentalStudy` instances in the database connecting a
the pair (`Paper`, `Dataset`).

Finally, each of the aforementioned resources can be tagged with custom `Keywords` and
related `Pathology`. Each `Pathology` can also be specified with an optional corresponding `Category`
(e.g. _Front of the Eye_, _Back of the Eye_).

## Configuration and Deployment

The system has been designed to allow for a flexible and customisable setup, depending on
the specific focus the collection of resources will be aiming to.

#### 1. Environment

This repository includes a `requirements.txt` file containing all the Python packages
and corresponding dependencies to setup the environment.

Once the **Python 3** environment has been created, to install the dependencies
within the environment it is required to execute the following command:

```bash

pip install -r requirements.txt

```

After having set up a working environment,
the following customisations may be also applied.

Most of the settings to change are included in `surv_ai/settings.py`.

#### 2. Database

The default setting for the database consider a `PostgreSQL` database
named `survai-repo`.

Database `USER`, `PASSWORD`, `HOST` and `PORT` should be configured as well.

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'survai-repo',
        'USER': 'kbai',
        'PASSWORD': 'kbai',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}
```

*WARNING:* Survai does not work with the standard sqlite3 database.
If you want you can spin a postgres database on the fly with

```
docker run -e POSTGRES_USER=kbai -e POSTGRES_PASSWORD=kbai -e POSTGRES_DB=survai-repo -p 5432:5432 -d postgres
```


#### 3. Front End specific Settings

The following settings allows for customisation to the platform **front-end**:

- `INDEX_TITLE`: Main title of the project
- `INDEX_SUBTITLE`: Subtitle of the project

Moreover, there are also **optional** settings for adding another logo and alt caption text
besides the default `MPBA` logo:

- `INDEX_ALT_LOGO_PATH` : (relative path to the `STATIC` folder) of an additional Logo to include in template
- `INDEX_ALT_LOGO_TEXT`: Caption Alt text of the logo image

#### 4. Back-end specific Settings

The following settings allows for customisation to the platform **back-end**:

- `ADMIN_SITE_HEADER`: Header title of the Back-end site
- `ADMIN_INDEX_TITLE`: Title to show in the Index Page of the back-end
- `ADMIN_SITE_TITLE`: Title of the Back-end site (also appears in the Login Form header)

##### 4.1 `AI-COLLECTION` App

The default name of the _Django_ app managing the creation of data and resources is
`SurvAI`.

This label will appear in the back-end main page in correspondence of the main panel of
the application. This label can also be customised by changin the value of the
`verbose_name` attribute of the `AeyeCollectionConfig` class:

(`ai_collection/apps.py`)

```python
from django.apps import AppConfig

class AeyeCollectionConfig(AppConfig):
    name = 'ai_collection'
    verbose_name = 'SurvAI'
```

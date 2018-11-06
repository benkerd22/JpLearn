## JpLearn

**A small Django app for learning Japanese words**

### Install

This app requires Django to work. If you havn't installed Django, try this [quick tutorial](https://docs.djangoproject.com/zh-hans/2.1/intro/install/).

At the root of your Django project:

    git clone https://github.com/benkerd22/JpLearn.git jplearn

Then edit your project's `settings.py` as follow:

    INSTALLED_APPS = [
        'jplearn.apps.JplearnConfig',
        ...
    ]

And your `urls.py`:

    urlpatterns = [
        path('jplearn/', include('jplearn.urls')),
        ...
    ]

After that, create the migration files and migrate them to your database:

    python3 manage.py makemigrations jplearn
    python3 manage.py migrate

And the app is ready to go !
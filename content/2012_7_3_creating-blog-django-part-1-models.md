Title: Creating a blog with django, part 1: models
Date: 2012-7-3 23:43
Modified:
Category: Blog
Tags: python, django, tutorials
Slug: creating-blog-django-part-1-models
Authors:
Summary: In this tutorial, I'll walk you through one possible way of creating a basic blog application using django 1.3's class-based generic views, built-in admin interface and syndication framework.

In this tutorial, I'll walk you through one possible way of creating a basic blog application using django 1.3's class-based generic views, built-in admin interface and syndication framework.

**Note: this tutorial was written for django 1.3, and is therefore out of date.**

I'll assume that you are familiar with some django fundamentals, specifically:

* Creating a new project
* Creating a new app
* Setting up a database and configuring django's database settings
* The basics of django models, templates, views, urlconfs etc.

If you aren't familiar with these things, then I suggest you work through the ['first steps' tutorial](https://docs.djangoproject.com/en/1.3/) on the [django website](https://www.djangoproject.com).

Start with an existing django project or create a new one, and make sure the database settings are up and running. We'll call the project directory `mysite` for convenience. Create a new app called `blog` and open `mysite/blog/models.py`. Our models will include a Post class to represent blog posts and a Tag class to represent the different categories a post can be placed in:

    #!python
    # models.py

    from django.db import models
    from datetime import datetime

    class Tag(models.Model):
        name = models.CharField(max_length=20, unique=True)

    class Post(models.Model):
        title = models.CharField(max_length=120)
        slug = models.SlugField(max_length=120, unique_for_date=\'publication_date\')
        publication_date = models.DateTimeField(default=datetime.now)
        body = models.TextField()
        tags = models.ManyToManyField(Tag)

Each `Tag` instance has only one attribute, a `name`, which is implemented as a `CharField` with a unique value (`unique=True`).

The `Post` class is somewhat more interesting. It has a `title` attribute, a main `body` of text a `publication_date` that defaults to the time at which the individual post was created.

The `tags` attribute implements a many-to-many relationship with `Tag`; Each blog post can fall under many categories, and each category can include many blog posts.

The `slug` attribute is a `SlugField`, which contains a 'slug' - a short, human-readable label for a blog post, used as part of its URL, and consisting only of letters, numbers, underscores and/or hyphens. Setting the `unique_for_date` option to `'publication_date'` ensures that no two blog posts can have both the same `publication_date` and the same `slug`.

Finally, append `'mysite.blog'` to `INSTALLED_APPS` in `settings.py`. Run `python manage.py validate` to check that your models are valid, and create the database tables corresponding to your models by typing `python manage.py syncdb.

Now you are ready for the next installment of this tutorial, which will intergrate our model with django's admin framework.

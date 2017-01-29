Creating a blog with django, part 2: admin interface
####################################################

:date: 2012-7-3 23:43
:modified:
:category: Blog
:tags: python, django, tutorials
:slug: creating-blog-django-part-2-admin-interface
:uniqueid: 2012-7-3-creating-blog-django-part-2-admin-interface-4065d8f7-22e9-4573-b48b-ad744f79d0c1
:summary: In part 1 of this series, we defined the models for our blog application. However, aside from `python manage.py shell`, we don't yet have a way to create and edit blog posts or categories. For this, we need to enable django's admin interface.

In `part2 <{filename}2012_7_3_creating-blog-django-part-1-models.md>`_ of this series, we defined the models for our blog application. However, aside from :code:`python manage.py shell`, we don't yet have a way to create and edit blog posts or categories. For this, we need to enable django's admin interface.

**Note: this tutorial was written for django 1.3, and is therefore out of date.**

If you haven't already done so, enable the admin interface by adding :code:`django.contrib.admin` to the :code:`INSTALLED_APPS` setting, and uncommenting the relevant lines in the main project urlconf, :code:`mysite/urls.py`.

.. code-block:: python
    :linenos: table

    from django.conf.urls.defaults import patterns, include, url

    # Uncomment the next two lines to enable the admin:
    from django.contrib import admin
    admin.autodiscover()

    urlpatterns = patterns('',
        # Examples:
        # url(r'^$', 'mysite.views.home', name='home'),
        # url(r'^mysite/', include('mysite.foo.urls')),

        # Uncomment the admin/doc line below to enable admin documentation:
        # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

        # Uncomment the next line to enable the admin:
        url(r'^admin/', include(admin.site.urls)),
    )

Create a file called :code:`admin.py` in the directory containing the blog app.

First, we need to import the admin module and the models which we wish to add to the admin interface.

.. code-block:: python
    :linenos: table

    # admin.py

    from django.contrib import admin
    from mysite.blog.models import Post, Tag

Next we register our models with the admin site.

.. code-block:: python
    :linenos: table
    :linenostart: 6

    admin.site.register(Post)
    admin.site.register(Tag)

At this point if you start the test server and go to `<http://127.0.0.1:8000/admin/>`_ you will see that the Post and Tag models have been added.

.. image:: {attach}images/django-admin1.png
    :alt: Screenshot of admin interface

However, if you create a couple of blog post and then try to view the list of posts, this is what you will see:

.. image:: {attach}images/django-admin2.png
    :alt: Screenshot of admin interface

.. image:: {attach}images/django-admin3.png
    :alt: Screenshot of admin interface


In order to rectify this, we need to add a :code:`__unicode__` method to each of our models.

.. code-block:: python
    :linenos: none

    # models.py

    class Post(models.Model):
    ....
        def __unicode__(self):
            return self.title

    class Tag(models.Model):
    ....
        def __unicode__(self):
            return self.name

Finally, we want the admin interface to generate the slug field automatically from the title field. To do this, we add the following lines to the admin.py file.

.. code-block:: python
    :linenos: table
    :linenostart: 6

    class PostAdmin(admin.ModelAdmin):
        prepopulated_fields = {"slug": ("title",)}

We then add 'PostAdmin' as the second argument to the call which registers Post with the admin interface.

.. code-block:: python
    :linenos: table
    :linenostart: 9

    admin.site.register(Post, PostAdmin)

Now you will see that the slug field is automatically filled in when you enter a title for your blog post. Here\'s the complete code for reference:

.. code-block:: python
    :linenos: table

    # admin.py

    from django.contrib import admin
    from mysite.blog.models import Post, Tag

    class PostAdmin(admin.ModelAdmin):
        prepopulated_fields = {"slug": ("title",)}

    admin.site.register(Post, PostAdmin)
    admin.site.register(Tag)

.. code-block:: python
    :linenos: table

    # models.py

    from django.db import models
    from datetime import datetime

    class Tag(models.Model):
        name = models.CharField(max_length=20, unique=True)

        def __unicode__(self):
            return self.name

    class Post(models.Model):
        title = models.CharField(max_length=120)
        slug = models.SlugField(max_length=120, unique_for_date='publication_date')
        publication_date = models.DateTimeField(default=datetime.now)
        body = models.TextField()
        tags = models.ManyToManyField(Tag)

        def __unicode__(self):
            return self.title

That concludes this installment. Next time we'll get to the real meat of the project - using Django's generic class-based views.

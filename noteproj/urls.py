from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib.auth.models import *
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'notes.views.index'),
    url(r'^submit/$', 'notes.views.submit'),
    url(r'^logout/$', 'notes.views.log_out'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r"^add_comment/(\d+)/$", "notes.views.add_comment"),
    url(r"^posts/(\d+)/$", "notes.views.post"),
    #url(r"^upvote/(\d+)/$", "notes.views.upvote"),
	url(r"^upvote/$", "notes.views.upvote"),
    url(r"^users/(?P<username>[\w-]+)/$", "notes.views.users"),
    url(r"^users/(?P<username>[\w-]+)/submitted/$", "notes.views.users"),
    url(r"^users/(?P<username>[\w-]+)/liked/$", "notes.views.liked"),
	url(r'^best/$', 'notes.views.best'),
	url(r'^new/$', 'notes.views.new'),
url(r'^trending/(?P<tag>[\w-]+)/$', 'notes.views.trending'),
    # url(r'^mysite/', include('mysite.foo.urls')),
	#url(r'^buses/$', 'buses.views.index'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),
)

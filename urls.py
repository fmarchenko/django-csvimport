from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^csvimport/(?P<label>.+)$', 'csvimport.views.csvimport', name="csvimport"),
    url(r'^csvdone/(?P<label>.+)$', 'csvimport.views.csvdump', name="csvdone"),
)

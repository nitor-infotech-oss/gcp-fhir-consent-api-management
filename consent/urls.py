from django.urls import re_path

from . import views

app_name = 'consent'

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^consentapproval/$', views.consentapproval, name='consentapproval'),
    re_path(r'^displaydata/(?P<requestid>[0-9]+)/$', views.displaydata, name='displaydata'),
    re_path(r'^manageresources/$', views.upload_resource, name='manageresources'),
    re_path(r'^capabilitystatement/$', views.get_capability_statement, name='capabilitystatement'),
]

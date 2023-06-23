from django.urls import re_path

from . import views

app_name = 'conformance'

urlpatterns = [
    re_path(r'^manageresources/$', views.upload_resource, name='manageresources'),
    re_path(r'^capabilitystatement/$', views.get_capability_statement, name='capabilitystatement'),
]

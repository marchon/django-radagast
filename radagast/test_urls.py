from django.conf.urls.defaults import patterns, url
from radagast import test_views

urlpatterns = patterns('',
    url('^test(?:/(?P<step>[\w-]+))?$',
        test_views.TestWizard.as_view(),
        name='test.view'),
)

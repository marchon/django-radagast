from django import http
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django.test import TestCase

import test_views


class TestURLs(TestCase):
    urls = 'radagast.test_urls'

    def setUp(self):
        self.w = test_views.TestWizard()
        self.n = test_views.NaughtyWizard()
        self.url = reverse('test.view')
        self.url_step = lambda x: reverse('test.view', args=[x])

    def test_reverse(self):
        assert self.url_step('one')

    def test_step(self):
        assert self.w.get_step('') == 'start'
        assert self.w.get_step('one') == 'one'
        self.assertRaises(http.Http404, self.w.get_step, 'four')

    def test_get(self):
        assert self.client.get(self.url).status_code == 200

    def test_not_ajax(self):
        assert 'html' in self.client.get(self.url).content

    def get_ajax(self, url):
        return self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    def _req(self, url, ssn):
        rf = RequestFactory()
        req = rf.get(self.url)
        req.session = ssn
        return req

    def test_track(self):
        ssn = {}
        get = self._req(self.url, ssn)
        self.w.dispatch(get)
        assert self.w.get_progress() == ['start']

        get_two = self._req(self.url_step('one'), ssn.copy())
        self.w.dispatch(get_two, 'one')
        assert self.w.get_progress() == ['start', 'one']

    def test_data(self):
        ssn = {}
        get = self._req(self.url, ssn)
        self.w.dispatch(get)
        self.w.set_data({'foo':'bar'})
        assert self.w.get_data() == {'foo': 'bar'}

        get = self._req(self.url_step('one'), ssn.copy())
        self.w.dispatch(get, 'one')
        self.w.set_data({'goo':False})
        assert self.w.get_data() == {'goo': False, 'foo': 'bar'}

    def test_not_reset(self):
        ssn = {}
        get = self._req(self.url, ssn)
        self.w.dispatch(get)
        self.w.set_data({'foo':'bar'})
        assert self.w.get_data() == {'foo': 'bar'}

        get = self._req(self.url, ssn.copy())
        self.w.dispatch(get)
        assert 'foo' in self.w.get_data()

    def test_reset(self):
        self.w.reset_on_start = True
        ssn = {}
        get = self._req(self.url, ssn)
        self.w.dispatch(get)
        self.w.set_data({'foo':'bar'})
        assert self.w.get_data() == {'foo': 'bar'}

        get = self._req(self.url, ssn.copy())
        self.w.dispatch(get)
        assert 'foo' not in self.w.get_data()

    def test_ajax(self):
        assert 'html' not in self.get_ajax(self.url).content

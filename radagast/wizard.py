from django import http
from django.views.generic.base import View

import jingo


class Storage(object):

    def __init__(self, request, name):
        self.name = name
        self.session = request.session
        self._new = {
            'progress': [],
            'data': {}
        }
        self.data = self.get()

    def reset(self):
        self.data = self._new.copy()
        self.set()

    def set(self):
        self.session[self.name] = self.data

    def get(self):
        return self.session.get(self.name, self._new.copy())


class Wizard(View):
    # If we should reset all the data accumulated in the wizard when
    # someone starts, defaults to no.
    reset_on_start = False
    # A SortedDict of the steps {name: view, ...}
    steps = {}
    # The path to the template you'd like to use as the wrapper.
    wrapper = ''

    def __init__(self, *args, **kw):
        self.name = 'wizard:%s' % self.__class__.__name__
        self.storage = None
        super(Wizard, self).__init__(*args, **kw)

    def dispatch(self, request, step='', *args, **kw):
        """
        Main entry point. Sets up the storage, resets it if needed.
        Finds the step, stores the progress. Then calls the appropriate
        method.
        """
        self.storage = Storage(request, self.name)
        if not step and self.reset_on_start:
            self.storage.reset()

        self.step = self.get_step(step)
        self.set_progress(self.step)
        kw['wizard'] = self
        return self.steps[self.step](request, *args, **kw)

    def set_data(self, data):
        """Place to store arbitrary data in the session for this wizard."""
        self.storage.get()['data'].update(data)
        self.storage.set()

    def get_data(self):
        return self.storage.get()['data']

    def set_progress(self, step):
        """Stores the progress of the user through the wizard."""
        progress = self.storage.get()['progress']
        if step not in progress:
            progress.append(step)
            self.storage.set()

    def get_progress(self):
        return self.storage.get()['progress']

    def get_step(self, step):
        """If no step is present, go to the start."""
        if not step:
            return self.steps.keys()[0]
        if step in self.steps:
            return step
        raise http.Http404

    def render(self, request, template, context):
        """
        Will render the template if using Ajax. If not will wrap the
        template in self.wrapper and use that.
        """
        context['wizard'] = self
        if request.is_ajax():
            return jingo.render(request, template, context)
        context['content'] = template
        return jingo.render(request, self.wrapper, context)

from radagast.wizard import Wizard
from django.utils.datastructures import SortedDict

def start(request, wizard):
    return wizard.render(request, 'radagast/start.html', {})


def one(request, wizard):
    return wizard.render(request, 'radagast/one.html', {})


class TestWizard(Wizard):
    steps = SortedDict((('start', start), ('one', one)))
    wrapper = 'radagast/wrapper.html'


class NaughtyWizard(Wizard):
    pass

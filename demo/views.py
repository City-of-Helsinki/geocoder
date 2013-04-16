from django.views.generic.base import TemplateView
from django.conf import settings

class DemoView(TemplateView):
    template_name = 'demo.html'

    def get_context_data(self, **kwargs):
        context = super(DemoView, self).get_context_data(**kwargs)
        prefix = getattr(settings, 'URL_PREFIX', '')
        context['API_PREFIX'] = '/' + prefix
        return context

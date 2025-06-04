from django.views.generic import TemplateView

from core.config import WebConfig


class AboutTemplateView(TemplateView):
    template_name = 'pages/about.html'

    def get_context_data(self: 'AboutTemplateView', **kwargs: dict):
        context = super().get_context_data(**kwargs)
        context['prefix'] = WebConfig.PREFIX
        return context

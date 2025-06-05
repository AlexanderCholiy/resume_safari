from core.config import WebConfig
from django.views.generic import TemplateView


class AboutTemplateView(TemplateView):
    template_name = 'pages/about.html'

    def get_context_data(self: 'AboutTemplateView', **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)
        context['prefix'] = WebConfig.PREFIX
        return context

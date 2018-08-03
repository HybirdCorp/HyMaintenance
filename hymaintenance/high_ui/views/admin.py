from django.views.generic import TemplateView

from .base import IsAdminTestMixin
from .base import get_context_data_dashboard_header


class AdminView(IsAdminTestMixin, TemplateView):
    template_name = "high_ui/admin.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        return context

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView

from customers.models import Company
from customers.models.user import get_companies_of_operator

from .base import get_context_data_dashboard_header


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "high_ui/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        return context

    def get(self, request, *args, **kwargs):
        self.user = request.user
        if self.user.is_superuser or self.user.is_staff:
            context = self.get_context_data(**kwargs)
            if self.user.is_superuser:
                context["companies"] = Company.objects.all()
            else:
                context["companies"] = get_companies_of_operator(self.user)

            # TODO prefetch the Company relations in one query for all companies:
            # 1) Company to its MaintenanceConsumers
            # 2) Company to its MaintenanceUsers

            return self.render_to_response(context)

        return redirect(self.user.company.get_absolute_url())

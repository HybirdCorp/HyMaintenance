from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.shortcuts import redirect
from django.views.generic import TemplateView

from customers.models import Company
from customers.models.user import get_active_companies_of_operator

from .base import get_context_data_dashboard_header


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "high_ui/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        return context

    def get(self, request, *args, **kwargs):
        self.user = request.user
        if self.user.has_operator_or_admin_permissions():
            context = self.get_context_data(**kwargs)
            if self.user.has_admin_permissions():
                context["companies"] = Company.objects.filter(is_archived=False).order_by(F("slug_name").asc())
            else:
                context["companies"] = get_active_companies_of_operator(self.user).order_by(F("slug_name").asc())

            # TODO prefetch the Company relations in one query for all companies:
            # 1) Company to its MaintenanceConsumers
            # 2) Company to its MaintenanceUsers

            return self.render_to_response(context)

        return redirect(self.user.company.get_absolute_url())

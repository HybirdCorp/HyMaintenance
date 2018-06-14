from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView

from customers.models import Company
from customers.models.user import MaintenanceUser
from customers.models.user import get_companies_of_operator


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "high_ui/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["maintainers"] = MaintenanceUser.objects.get_active_operator_users_queryset()
        return context

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_staff:
            context = self.get_context_data(**kwargs)
            if user.is_superuser:
                context["companies"] = Company.objects.all()
            else:
                context["companies"] = get_companies_of_operator(user)

            # TODO prefetch the Company relations in one query for all companies:
            # 1) Company to its MaintenanceConsumers
            # 2) Company to its MaintenanceUsers

            return self.render_to_response(context)

        return redirect(user.company.get_absolute_url())

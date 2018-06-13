from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView

from customers.models import Company
from customers.models import MaintenanceUser
from maintenance.forms.project import ProjectCreateForm
from maintenance.forms.project import ProjectUpdateForm
from maintenance.models import MaintenanceType

from .base import LoginRequiredMixin
from .base import ViewWithCompany


class ProjectCreateView(FormView):
    form_class = ProjectCreateForm
    template_name = "high_ui/forms/create_project.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        user = self.request.user
        if not user.is_staff:
            raise Http404(
                _("No %(verbose_name)s found matching the query") % {"verbose_name": Company._meta.verbose_name}
            )
        context = super().get_context_data(**kwargs)
        context["maintenance_types"] = MaintenanceType.objects.order_by("id")
        context["companies"] = Company.objects.all()
        context["maintainers"] = MaintenanceUser.objects.get_operator_users_queryset()
        return context

    def form_valid(self, form):
        form.create_company_and_contracts()
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, ViewWithCompany, FormView):
    form_class = ProjectUpdateForm
    template_name = "high_ui/forms/update_project.html"
    success_url = "/"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def form_valid(self, form):
        form.update_company_and_contracts()
        return super().form_valid(form)

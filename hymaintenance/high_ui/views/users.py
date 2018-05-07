from django.views.generic import CreateView

from customers.forms import ManagerUserCreateForm, OperatorUserCreateForm
from maintenance.forms import MaintenanceConsumerCreateForm

from .base import CreateViewWithCompany, LoginRequiredMixin


class ConsumerCreateView(LoginRequiredMixin, CreateViewWithCompany):
    form_class = MaintenanceConsumerCreateForm
    template_name = "high_ui/forms/add_consumer.html"


class ManagerUserCreateView(LoginRequiredMixin, CreateViewWithCompany):
    form_class = ManagerUserCreateForm
    template_name = "high_ui/forms/add_user.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_label'] = "Nouveau manager"
        context['form_submit_label'] = "Ajouter ce manager"
        return context


class OperatorUserCreateView(LoginRequiredMixin, CreateViewWithCompany):
    form_class = OperatorUserCreateForm
    template_name = "high_ui/forms/add_user.html"

    # TMP: Technically, only the template needs the Company right now, so don't send it to the form init.
    # This is done until we have the concept of "maintenance providers" or "projects" which this view/form
    # will need to link the MaintenanceUser to this Company as the "maintainer"
    # Until then, the view/form have the company but the MaintenanceUser created will not use it
    def get_form_kwargs(self):
        return super(CreateView, self).get_form_kwargs()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_label'] = "Nouvel intervenant"
        context['form_submit_label'] = "Ajouter cet intervenant"
        return context

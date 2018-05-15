from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView, TemplateView

from customers.forms import ManagerUserCreateForm, OperatorUserArchiveForm, OperatorUserCreateForm, OperatorUserUnarchiveForm
from customers.models import Company
from customers.models.user import MaintenanceUser, get_companies_of_operator
from maintenance.forms.consumer import MaintenanceConsumerCreateForm

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_label'] = "Nouvel intervenant"
        context['form_submit_label'] = "Ajouter cet intervenant"
        return context


class OperatorUsersUpdateView(LoginRequiredMixin, TemplateView):
    template_name = "high_ui/forms/update_operators.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["maintainers"] = MaintenanceUser.objects.get_operator_users_queryset()
        context["archive_form"] = OperatorUserArchiveForm()
        context["unarchive_form"] = OperatorUserUnarchiveForm()
        context["active_operators_number"] = context["maintainers"].filter(is_active=True).count()
        context["archived_operators_number"] = context["maintainers"].filter(is_active=False).count()
        return context

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_staff:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': Company._meta.verbose_name})
        context = self.get_context_data(**kwargs)
        context["companies"] = get_companies_of_operator(user)

        return self.render_to_response(context)


class OperatorUsersArchiveView(LoginRequiredMixin, FormView):
    form_class = OperatorUserArchiveForm
    success_url = "/"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class OperatorUsersUnarchiveView(LoginRequiredMixin, FormView):
    form_class = OperatorUserUnarchiveForm
    success_url = "/"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

from django.contrib.auth import decorators
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, View

from customers.models import Company
from maintenance.models import IncomingChannel, MaintenanceContract, MaintenanceType


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **kwargs):
        view = super(LoginRequiredMixin, cls).as_view(**kwargs)
        return decorators.login_required(view)


class ViewWithCompany(View):
    pk_url_kwarg = "company_name"

    def dispatch(self, request, *args, **kwargs):
        self.company = self.get_company()
        return super().dispatch(request, *args, **kwargs)

    def get_company(self):
        user = self.request.user
        company = get_object_or_404(Company, slug_name=self.kwargs.get(self.pk_url_kwarg))
        if not user.is_staff or company not in user.operator_for.all():
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': Company._meta.verbose_name})
        return company

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["maintenance_types"] = MaintenanceType.objects.order_by("id")
        context['channels'] = IncomingChannel.objects.all()
        contracts = MaintenanceContract.objects.filter(company=self.company, disabled=False)
        context['contracts'] = contracts
        context['company'] = self.company
        return context


class CreateViewWithCompany(ViewWithCompany, CreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.company
        contracts = MaintenanceContract.objects.filter(company=self.company, disabled=False)
        context['contracts'] = contracts
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.company
        return kwargs

    def get_success_url(self):
        return reverse('high_ui:dashboard')

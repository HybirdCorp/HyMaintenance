
from django.urls import reverse
from django.views.generic import UpdateView

from ..forms import GeneralInformationModelForm
from ..models import GeneralInformation
from .base import IsAdminTestMixin
from .base import get_context_data_dashboard_header
from .base import get_context_data_footer


class GeneralInformationUpdateView(IsAdminTestMixin, UpdateView):
    form_class = GeneralInformationModelForm
    template_name = "high_ui/forms/update_infos.html"
    model = GeneralInformation

    def get_success_url(self):
        return reverse("high_ui:admin")

    def get_object(self, queryset=None):
        return GeneralInformation.objects.all().first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        context.update(get_context_data_footer())
        return context

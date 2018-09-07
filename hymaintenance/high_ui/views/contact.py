
from django.views.generic import TemplateView

from .base import IsAtLeastAllowedManagerTestMixin
from .base import ViewWithCompany


class ContactView(ViewWithCompany, IsAtLeastAllowedManagerTestMixin, TemplateView):
    template_name = "high_ui/contact.html"

from customers.fields import LowerCaseEmailField

from django.db import models
from django.utils.translation import ugettext_lazy as _


class GeneralInformation(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    email = LowerCaseEmailField(_("Email address"), max_length=255)
    address = models.TextField(_("postal address"))
    website = models.CharField(_("Website"), max_length=255)
    phone = models.CharField(_("phone number"), max_length=25, blank=True, null=True)

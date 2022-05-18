from django.db import models
from django.utils.translation import ugettext_lazy as _


class MaintenanceType(models.Model):
    CSS_CLASSES = ("type-maintenance", "type-support", "type-correction")
    FORM_LABELS = (_("Green counter"), _("Blue counter"), _("Grey counter"))

    name = models.CharField(_("Name"), max_length=255)
    default_visibility = models.BooleanField(_("Visible to manager"), default=True)

    class Meta:
        verbose_name = _("Maintenance's Type")
        verbose_name_plural = _("Maintenance's Types")

    def css_class(self):
        return MaintenanceType.CSS_CLASSES[self.id - 1]

    @property
    def form_label(self):
        return MaintenanceType.FORM_LABELS[self.id - 1]

    def __str__(self):
        return "%s" % self.name


class IncomingChannel(models.Model):
    name = models.CharField(_("Name of Incoming Channel"), max_length=255)

    class Meta:
        verbose_name = _("Maintenance's Incoming Channel")
        verbose_name_plural = _("Maintenance's Incoming Channel")

    def __str__(self):
        return "%s" % self.name

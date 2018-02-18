from django.db import models
from django.utils.translation import ugettext_lazy as _

from customers.models import Company, MaintenanceUser

from .consumer import MaintenanceConsumer
from .other_models import IncomingChannel, MaintenanceType


class MaintenanceIssue(models.Model):
    company = models.ForeignKey(Company, verbose_name=_("Company"))
    consumer_who_ask = models.ForeignKey(MaintenanceConsumer, verbose_name="Who ask the question ?", null=True, blank=True,
                                         related_name="consumers_who_asked")

    user_who_fix = models.ForeignKey(MaintenanceUser, verbose_name="Who fix the issue ? ", null=True, blank=True,
                                     related_name="users_who_fixed")
    incoming_channel = models.ForeignKey(IncomingChannel, verbose_name="Incoming Channel", null=True, blank=True)

    subject = models.CharField(_("Subject"), max_length=500, default="une question")
    date = models.DateField(_("Issue Date"))
    maintenance_type = models.ForeignKey(MaintenanceType)
    description = models.TextField(null=True, blank=True)

    number_minutes = models.PositiveIntegerField(default=0, blank=True)
    resolution_date = models.DateTimeField(null=True, blank=True)
    shipping_date = models.DateTimeField(null=True, blank=True)
    answer = models.TextField(null=True, blank=True)

    fields_for_form = ('consumer_who_ask', 'user_who_fix', 'incoming_channel',
                       'subject', 'date', 'maintenance_type', 'description',
                       'resolution_date', 'shipping_date', 'answer')

    def __str__(self):
        return "Date : %s, Subject :%s For : %s , Type :%s " % (self.date.strftime("%d/%m/%Y at %H:%M"),
                                                                self.subject,
                                                                self.company, self.maintenance_type)

    def get_hours(self):
        return self.number_minutes / 60

    def who_ask(self):
        if self.consumer_who_ask:
            return self.consumer_who_ask.name
        return ""

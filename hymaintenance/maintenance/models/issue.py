from django.db import models
from django.utils.translation import ugettext_lazy as _

from customers.models import Company, MaintenanceUser

from .consumer import MaintenanceConsumer
from .other_models import IncomingChannel, MaintenanceType


class MaintenanceIssue(models.Model):
    company_issue_number = models.PositiveIntegerField(verbose_name=_("Issue number"))
    company = models.ForeignKey(Company, verbose_name=_("Company"), on_delete=models.PROTECT)
    consumer_who_ask = models.ForeignKey(MaintenanceConsumer, verbose_name="Who ask the question ?", null=True, blank=True,
                                         related_name="consumers_who_asked", on_delete=models.PROTECT)

    user_who_fix = models.ForeignKey(MaintenanceUser, verbose_name="Who fix the issue ? ", null=True, blank=True,
                                     related_name="users_who_fixed", on_delete=models.PROTECT)
    incoming_channel = models.ForeignKey(IncomingChannel, verbose_name="Incoming Channel", null=True, blank=True,
                                         on_delete=models.PROTECT)

    subject = models.CharField(_("Subject"), max_length=500, default="une question")
    date = models.DateField(_("Issue Date"))
    maintenance_type = models.ForeignKey(MaintenanceType, on_delete=models.PROTECT)
    description = models.TextField(null=True, blank=True)

    number_minutes = models.PositiveIntegerField(default=0, blank=True)
    resolution_date = models.DateTimeField(null=True, blank=True)
    shipping_date = models.DateTimeField(null=True, blank=True)
    answer = models.TextField(null=True, blank=True)

    fields_for_form = ('consumer_who_ask', 'user_who_fix', 'incoming_channel',
                       'subject', 'date', 'maintenance_type', 'description',
                       'resolution_date', 'shipping_date', 'answer')

    class Meta:
        verbose_name = "Issue"
        verbose_name_plural = "Issues"
        unique_together = [["company_issue_number", "company"]]

    def __str__(self):
        return "Date : %s, Subject :%s For : %s , Type :%s " % (self.date.strftime("%d/%m/%Y at %H:%M"),
                                                                self.subject,
                                                                self.company, self.maintenance_type)

    def get_counter_name(self):
        counter_name = self.company.contracts.filter(maintenance_type=self.maintenance_type).first().counter_name
        return counter_name if counter_name != "" else self.maintenance_type.name

    def get_hours(self):
        return self.number_minutes / 60

    def who_ask(self):
        if self.consumer_who_ask:
            return self.consumer_who_ask.name
        return ""

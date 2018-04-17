import os

from django.conf import settings
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from customers.models import Company, MaintenanceUser

from .consumer import MaintenanceConsumer
from .other_models import IncomingChannel, MaintenanceType


def _get_file_path(instance, filename):
    file_path = os.path.join(*['upload', instance.company.slug_name, "issue-" + str(instance.company_issue_number), filename])
    print(os.path.join(settings.MEDIA_ROOT, file_path))
    if os.path.exists(os.path.join(*[settings.MEDIA_ROOT, file_path])):
        file_path = os.path.join(*['upload', instance.company.slug_name, "issue-" + str(instance.company_issue_number), "2-" + filename])
    return file_path


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
    context_description_file = models.FileField(null=True, upload_to=_get_file_path)
    resolution_description_file = models.FileField(null=True, upload_to=_get_file_path)

    fields_for_form = ('consumer_who_ask', 'user_who_fix', 'incoming_channel',
                       'subject', 'date', 'maintenance_type', 'description',
                       'resolution_date', 'shipping_date', 'answer', 'context_description_file',
                       'resolution_description_file')

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

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.id is None:
            Company.objects.filter(id=self.company_id).update(issues_counter=models.F('issues_counter') + 1)
            self.company_issue_number = Company.objects.filter(id=self.company_id).values_list('issues_counter', flat=True).first()
        else:
            this = MaintenanceIssue.objects.get(id=self.id)
            if this.context_description_file is not None and this.context_description_file != self.context_description_file:
                this.context_description_file.delete(save=False)
            if this.resolution_description_file is not None and this.resolution_description_file != self.resolution_description_file:
                this.resolution_description_file.delete(save=False)
        super().save(*args, **kwargs)

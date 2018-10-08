import os

from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from customers.models import Company
from customers.models import MaintenanceUser

from .consumer import MaintenanceConsumer
from .other_models import IncomingChannel
from .utils import get_counter_name


class MaintenanceIssueAttachmentStorage(FileSystemStorage):
    def _save(self, name, content):
        if self.exists(name):
            self.delete(name)
        return super()._save(name, content)

    def get_available_name(self, name, max_length=None):
        return name


def _get_context_file_path(instance, filename):
    return os.path.join(
        "upload", instance.company.slug_name, "issue-" + str(instance.company_issue_number), "context", filename
    )


def _get_resolution_file_path(instance, filename):
    return os.path.join(
        "upload", instance.company.slug_name, "issue-" + str(instance.company_issue_number), "resolution", filename
    )


class MaintenanceIssue(models.Model):
    company_issue_number = models.PositiveIntegerField(verbose_name=_("Issue number"))
    company = models.ForeignKey(Company, verbose_name=_("Company"), on_delete=models.PROTECT)
    consumer_who_ask = models.ForeignKey(
        MaintenanceConsumer,
        verbose_name=_("Author"),
        null=True,
        blank=True,
        related_name="consumers_who_asked",
        on_delete=models.PROTECT,
    )

    user_who_fix = models.ForeignKey(
        MaintenanceUser,
        verbose_name=_("Operator"),
        null=True,
        blank=True,
        related_name="users_who_fixed",
        on_delete=models.PROTECT,
    )
    incoming_channel = models.ForeignKey(
        IncomingChannel, verbose_name=_("Incoming Channel"), null=True, blank=True, on_delete=models.PROTECT
    )

    subject = models.CharField(_("Subject"), max_length=500, default="une question")
    date = models.DateField(_("Issue Date"))
    contract = models.ForeignKey(
        to="maintenance.MaintenanceContract", verbose_name=_("Type of activity"), on_delete=models.PROTECT
    )
    description = models.TextField(_("Details"), null=True, blank=True)

    number_minutes = models.PositiveIntegerField(_("Time spent"), default=0, blank=True)
    resolution_date = models.DateTimeField(_("Resolution date"), null=True, blank=True)
    shipping_date = models.DateTimeField(_("Delivery date"), null=True, blank=True)
    answer = models.TextField(_("Comments"), null=True, blank=True)
    context_description_file = models.FileField(
        _("Attachment"),
        null=True,
        blank=True,
        max_length=200,
        storage=MaintenanceIssueAttachmentStorage(),
        upload_to=_get_context_file_path,
    )
    resolution_description_file = models.FileField(
        _("Attachment"),
        null=True,
        blank=True,
        max_length=200,
        storage=MaintenanceIssueAttachmentStorage(),
        upload_to=_get_resolution_file_path,
    )

    fields_for_form = (
        "consumer_who_ask",
        "user_who_fix",
        "incoming_channel",
        "subject",
        "date",
        "contract",
        "description",
        "resolution_date",
        "shipping_date",
        "answer",
        "context_description_file",
        "resolution_description_file",
    )

    class Meta:
        verbose_name = "Issue"
        verbose_name_plural = "Issues"
        unique_together = [["company_issue_number", "company"]]

    def __str__(self):
        return _("Date: {date}, Subject: {subject}, For: {company} , Type: {contract} ").format(
            date=self.date.strftime(str(_("%m/%d/%Y at %H:%M"))),
            subject=self.subject,
            company=self.company,
            contract=self.contract,
        )

    def get_counter_name(self):
        return get_counter_name(self)

    def get_hours(self):
        return self.number_minutes / 60

    def who_ask(self):
        if self.consumer_who_ask:
            return self.consumer_who_ask.name
        return ""

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.id is None:
            Company.objects.filter(id=self.company_id).update(issues_counter=models.F("issues_counter") + 1)
            self.company_issue_number = (
                Company.objects.filter(id=self.company_id).values_list("issues_counter", flat=True).first()
            )
        super().save(*args, **kwargs)

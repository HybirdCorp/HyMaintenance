from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _


class Company(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    slug_name = models.SlugField(editable=False, unique=True, max_length=255)
    issues_counter = models.PositiveIntegerField(default=0)
    is_archived = models.BooleanField(_("Archived"), default=False)
    contact = models.ForeignKey(
        to="customers.MaintenanceUser",
        verbose_name=_("Contact"),
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="contact_of",
    )

    __original_name = None

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("high_ui:project_details", args=[self.slug_name])

    # NOT SAFE if two namesake companies are created in the same time, it could raise IntegrityError on slug_name
    def slugify_company_name(self):
        slugified_name = slugify(self.name)
        counter = 1
        while Company.objects.filter(slug_name=slugified_name):
            counter += 1
            slugified_name = slugify(self.name) + str(counter)
        return slugified_name

    def save(self, *args, **kwargs):
        if self.id is not None:
            if self.__original_name != self.name:
                self.slug_name = self.slugify_company_name()
                super().save(update_fields=["name", "slug_name", "contact", "is_archived"])
            super().save(update_fields=["name", "contact", "is_archived"])
        else:
            self.slug_name = self.slugify_company_name()
            super().save(*args, **kwargs)
        self.__original_name = self.name

    def get_operators_choices(self):
        return [(operator.pk, operator.get_full_name()) for operator in self.managed_by.all()]

    def get_active_operators_choices(self):
        return [(operator.pk, operator.get_full_name()) for operator in self.managed_by.filter(is_active=True)]

    def archive(self):
        self.is_archived = True
        self.save()

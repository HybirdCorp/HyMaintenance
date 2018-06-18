from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Company(models.Model):
    name = models.CharField("name", max_length=255)
    slug_name = models.SlugField(editable=False, unique=True, max_length=255)
    maintenance_contact = models.CharField("name of internal contact", max_length=500)
    issues_counter = models.PositiveIntegerField(default=0)

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
                super().save(update_fields=["name", "maintenance_contact", "slug_name"])
            super().save(update_fields=["name", "maintenance_contact"])
        else:
            self.slug_name = self.slugify_company_name()
            super().save(*args, **kwargs)
        self.__original_name = self.name

    def get_operators_choices(self):
        return [(operator.pk, operator.get_full_name()) for operator in self.managed_by.all()]

    def get_active_operators_choices(self):
        return [(operator.pk, operator.get_full_name()) for operator in self.managed_by.filter(is_active=True)]

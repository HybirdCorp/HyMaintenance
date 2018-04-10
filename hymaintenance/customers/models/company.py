from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Company(models.Model):
    name = models.CharField("name", max_length=255)
    slug_name = models.SlugField(editable=False, unique=True, max_length=255)
    maintenance_contact = models.CharField("name of internal contact",
                                           max_length=500)
    issues_counter = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('high_ui:company-details', args=[self.pk])

    def save(self, *args, **kwargs):
        if self.id is not None:
            super().save(update_fields=['name', 'maintenance_contact'])
        else:
            # NOT SAFE if two namesake companies are created in the same time, it could raise IntegrityError on slug_name
            slugified_name = slugify(self.name)
            counter = 1
            while(Company.objects.filter(slug_name=slugified_name)):
                counter += 1
                slugified_name = slugify(self.name) + str(counter)
            self.slug_name = slugified_name
            super().save(*args, **kwargs)

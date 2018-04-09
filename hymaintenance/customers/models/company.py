from django.db import models
from django.urls import reverse


class Company(models.Model):
    name = models.CharField("name", max_length=255)
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
            super().save(*args, **kwargs)
